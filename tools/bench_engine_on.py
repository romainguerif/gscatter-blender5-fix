# Benchmark "moteur allumé en permanence" — à lancer dans Blender (Scripting > Run Script)
# Construit une scène de stress : N instances d'un objet ~5k polys via Geometry Nodes,
# configure Cycles en mode "Clarisse-like" (persistent data, culling, viewport léger).
#
# Protocole :
#   1. Lancer avec INSTANCE_COUNT = 500_000 → naviguer en Solid (ça doit ramer/geler)
#   2. Passer en Rendered (Z > Rendered) → naviguer : fluide
#   3. Monter INSTANCE_COUNT (5M, 20M, 50M...) et noter où l'init/RAM décroche
#
import bpy
import time

INSTANCE_COUNT = 500_000   # monter progressivement : 5_000_000, 20_000_000...
AREA_SIZE = 2000.0         # terrain en mètres

t0 = time.perf_counter()

# --- nettoyage ---
for obj in [o for o in bpy.data.objects if o.name.startswith("BENCH_")]:
    bpy.data.objects.remove(obj, do_unlink=True)

# --- asset ~5k polys (équivalent du test Geo-Scatter) ---
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=4, radius=1.0)  # 5120 tris
asset = bpy.context.object
asset.name = "BENCH_asset"
asset.hide_render = False

# --- terrain ---
bpy.ops.mesh.primitive_plane_add(size=AREA_SIZE)
ground = bpy.context.object
ground.name = "BENCH_ground"

# --- geometry nodes : distribute + instance (jamais réalisé) ---
mod = ground.modifiers.new("BENCH_scatter", "NODES")
tree = bpy.data.node_groups.new("BENCH_scatter_tree", "GeometryNodeTree")
mod.node_group = tree

tree.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
tree.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")

n_in = tree.nodes.new("NodeGroupInput")
n_out = tree.nodes.new("NodeGroupOutput")
n_dist = tree.nodes.new("GeometryNodeDistributePointsOnFaces")
n_obj = tree.nodes.new("GeometryNodeObjectInfo")
n_inst = tree.nodes.new("GeometryNodeInstanceOnPoints")

n_obj.inputs["Object"].default_value = asset
n_obj.transform_space = "RELATIVE"
n_obj.inputs["As Instance"].default_value = True  # CRUCIAL : sinon la géométrie est réalisée

density = INSTANCE_COUNT / (AREA_SIZE * AREA_SIZE)
n_dist.inputs["Density"].default_value = density

links = tree.links
links.new(n_in.outputs["Geometry"], n_dist.inputs["Mesh"])
links.new(n_dist.outputs["Points"], n_inst.inputs["Points"])
links.new(n_obj.outputs["Geometry"], n_inst.inputs["Instances"])
links.new(n_inst.outputs["Instances"], n_out.inputs["Geometry"])

# cacher l'asset source
asset.hide_set(True)

# --- config Cycles "Clarisse-like" ---
scene = bpy.context.scene
scene.render.engine = "CYCLES"
cy = scene.cycles
prefs = bpy.context.preferences.addons.get("cycles")
if prefs:  # GPU si dispo
    try:
        cprefs = prefs.preferences
        for dt in ("OPTIX", "METAL", "CUDA", "HIP"):
            try:
                cprefs.compute_device_type = dt
                break
            except TypeError:
                continue
        for d in cprefs.devices:
            d.use = True
        cy.device = "GPU"
    except Exception as e:
        print("GPU non configuré :", e)

scene.render.use_persistent_data = True          # scène résidente entre les syncs
cy.preview_samples = 16
cy.use_preview_denoising = True
cy.use_preview_adaptive_sampling = True

# culling natif Cycles (équivalent moteur des options Geo-Scatter)
scene.render.use_simplify = True
cy.use_camera_cull = True
cy.camera_cull_margin = 0.1
cy.use_distance_cull = True
cy.distance_cull_margin = 500.0
for obj in (ground,):
    obj.cycles.use_camera_cull = True
    obj.cycles.use_distance_cull = True

t1 = time.perf_counter()
print(f"[BENCH] scène construite : {INSTANCE_COUNT:,} instances × 5120 tris "
      f"= {INSTANCE_COUNT * 5120 / 1e9:.1f} milliards de tris virtuels, en {t1 - t0:.2f}s")
print("[BENCH] 1) Navigue en Solid → note le FPS.  2) Z > Rendered → compare.")
print("[BENCH] 3) Chronomètre la première synchro Cycles (console : 'Synchronizing object').")
