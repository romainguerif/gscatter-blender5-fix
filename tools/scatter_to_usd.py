# Scatter → USD PointInstancer — bake les scatters Blender (GScatter, Geo-Scatter,
# n'importe quel système d'instances) vers une stage USD ouvrable dans Solaris/usdview.
#
# Usage dans Blender :
#   1. Sélectionner le/les objets scatter (les surfaces portant le modificateur)
#   2. Scripting > ouvrir ce fichier > Run Script
#   → écrit OUTPUT_DIR/scatter_bake.usda (+ prototypes.usd avec matériaux)
#
# Le viewport peut rester en Bounds/airbag : l'évaluation se fait via le depsgraph,
# sans jamais dessiner les instances.
#
import bpy
import os
import time
from collections import defaultdict

OUTPUT_DIR = os.path.expanduser("~/Desktop/scatter_usd")
STAGE_NAME = "scatter_bake.usda"
PROTOS_NAME = "prototypes.usd"

try:
    from pxr import Usd, UsdGeom, Gf, Vt, Sdf
except ImportError:
    raise RuntimeError(
        "Module pxr introuvable — ce Blender n'embarque pas les bindings Python USD. "
        "Vérifie que tu utilises un build officiel 4.2+."
    )

os.makedirs(OUTPUT_DIR, exist_ok=True)
t0 = time.perf_counter()

sources = [o for o in bpy.context.selected_objects] or list(bpy.context.scene.objects)
source_names = {o.name for o in sources}

depsgraph = bpy.context.evaluated_depsgraph_get()

# --- collecte : une passe sur les instances évaluées du depsgraph ---------
# clé = l'objet instancié (le prototype), valeurs = transforms
positions = defaultdict(list)
orientations = defaultdict(list)
scales = defaultdict(list)
proto_objects = {}

for inst in depsgraph.object_instances:
    if not inst.is_instance:
        continue
    parent = inst.parent.original if inst.parent else None
    if parent is None or parent.name not in source_names:
        continue
    proto = inst.instance_object.original
    if proto.type != "MESH":
        continue
    key = proto.name
    proto_objects[key] = proto

    m = inst.matrix_world
    loc, rot, sca = m.decompose()
    positions[key].append(Gf.Vec3f(loc.x, loc.y, loc.z))
    # USD attend des quaternions half — ordre (i, j, k, w) via Gf.Quath(w, i, j, k)
    orientations[key].append(Gf.Quath(rot.w, rot.x, rot.y, rot.z))
    scales[key].append(Gf.Vec3f(sca.x, sca.y, sca.z))

total = sum(len(v) for v in positions.values())
if total == 0:
    raise RuntimeError("Aucune instance trouvée sur les objets sélectionnés.")

t1 = time.perf_counter()
print(f"[USD] {total:,} instances collectées ({len(proto_objects)} prototypes) en {t1 - t0:.1f}s")

# --- export des prototypes (avec matériaux) via l'exporteur USD de Blender ---
protos_path = os.path.join(OUTPUT_DIR, PROTOS_NAME)
prev_selection = [o for o in bpy.context.selected_objects]
bpy.ops.object.select_all(action="DESELECT")
for proto in proto_objects.values():
    proto.hide_set(False)
    proto.select_set(True)
bpy.ops.wm.usd_export(
    filepath=protos_path,
    selected_objects_only=True,
    export_materials=True,
    export_textures=True,
    use_instancing=False,
)
bpy.ops.object.select_all(action="DESELECT")
for o in prev_selection:
    o.select_set(True)

t2 = time.perf_counter()
print(f"[USD] prototypes exportés → {protos_path} en {t2 - t1:.1f}s")


def sanitize(name):
    return "".join(c if c.isalnum() or c == "_" else "_" for c in name)


# --- stage principale : un PointInstancer regroupant tous les prototypes ----
stage_path = os.path.join(OUTPUT_DIR, STAGE_NAME)
stage = Usd.Stage.CreateNew(stage_path)
UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.z)   # convention Blender
UsdGeom.SetStageMetersPerUnit(stage, 1.0)

root = UsdGeom.Xform.Define(stage, "/World")
stage.SetDefaultPrim(root.GetPrim())

instancer = UsdGeom.PointInstancer.Define(stage, "/World/Scatter")

proto_keys = sorted(positions.keys())
proto_paths = []
protos_scope = UsdGeom.Scope.Define(stage, "/World/Prototypes")
for key in proto_keys:
    prim_path = f"/World/Prototypes/{sanitize(key)}"
    proto_prim = stage.DefinePrim(prim_path, "Xform")
    # référence vers l'objet dans le fichier de prototypes
    proto_prim.GetReferences().AddReference(
        f"./{PROTOS_NAME}", f"/root/{sanitize(key)}"
    )
    proto_paths.append(prim_path)

# les prototypes ne doivent pas être rendus en dehors de l'instancer
protos_scope.GetPrim().SetSpecifier(Sdf.SpecifierOver)
UsdGeom.Imageable(protos_scope.GetPrim()).MakeInvisible()

instancer.CreatePrototypesRel().SetTargets(proto_paths)

all_pos, all_orient, all_scale, all_idx = [], [], [], []
for i, key in enumerate(proto_keys):
    n = len(positions[key])
    all_pos.extend(positions[key])
    all_orient.extend(orientations[key])
    all_scale.extend(scales[key])
    all_idx.extend([i] * n)
    print(f"[USD]   proto {i}: {key} × {n:,}")

instancer.CreatePositionsAttr(Vt.Vec3fArray(all_pos))
instancer.CreateOrientationsAttr(Vt.QuathArray(all_orient))
instancer.CreateScalesAttr(Vt.Vec3fArray(all_scale))
instancer.CreateProtoIndicesAttr(Vt.IntArray(all_idx))

stage.GetRootLayer().Save()

t3 = time.perf_counter()
print(f"[USD] stage écrite → {stage_path} en {t3 - t2:.1f}s (total {t3 - t0:.1f}s)")
print(f"[USD] Ouvre-la dans Solaris : File > Import > USD, ou usdview '{stage_path}'")
