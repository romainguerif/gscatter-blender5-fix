bl_info = {
    "name": "Render Lock — moteur toujours allumé",
    "author": "Romain + Claude",
    "version": (0, 2),
    "blender": (4, 2, 0),
    "location": "View3D > N-panel > Render Lock",
    "description": "Force le viewport Rendered (Cycles), airbag Bounds en Solid, désarme le pie menu Z",
    "category": "3D View",
}

import bpy
from bpy.app.handlers import persistent

# ---------------------------------------------------------------------------
# Réglages
# ---------------------------------------------------------------------------
# "AIRBAG"  : autorise Solid, mais les objets lourds restent des bounding boxes
# "REVERT"  : re-force le mode Rendered dès qu'on en sort (verrou total)
GUARD_MODE = "AIRBAG"

# Un objet est considéré "lourd" s'il porte un modificateur Geometry Nodes
# dont le nom contient un de ces mots-clés (GScatter, Geo-Scatter, bench…)
HEAVY_KEYWORDS = ("gscatter", "scatter", "bench")

_msgbus_owner = object()


def _is_heavy(obj):
    if obj.display_type == "BOUNDS":
        return True
    for mod in obj.modifiers:
        if mod.type == "NODES" and any(k in mod.name.lower() for k in HEAVY_KEYWORDS):
            return True
    return False


def _arm_airbag():
    """Objets lourds → affichage Bounds. Sans effet sur le rendu Cycles."""
    count = 0
    for obj in bpy.data.objects:
        if obj.type == "MESH" and _is_heavy(obj) and obj.display_type != "BOUNDS":
            obj.display_type = "BOUNDS"
            count += 1
    return count


def _force_rendered():
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type != "VIEW_3D":
                continue
            for space in area.spaces:
                if space.type == "VIEW_3D":
                    if space.shading.type != "RENDERED":
                        space.shading.type = "RENDERED"
                    # les outlines de sélection coûtent cher sur les grosses instances
                    space.overlay.show_outline_selected = False


def _clarisse_settings(scene):
    scene.render.engine = "CYCLES"
    scene.render.use_persistent_data = True
    cy = scene.cycles
    cy.preview_samples = 16
    cy.use_preview_denoising = True
    cy.use_preview_adaptive_sampling = True


def _on_shading_changed():
    if GUARD_MODE == "REVERT":
        # repasse en Rendered au prochain tick (on ne peut pas écrire pendant le callback)
        bpy.app.timers.register(_force_rendered, first_interval=0.0)
    else:
        _arm_airbag()


def _subscribe():
    bpy.msgbus.clear_by_owner(_msgbus_owner)
    bpy.msgbus.subscribe_rna(
        key=(bpy.types.View3DShading, "type"),
        owner=_msgbus_owner,
        args=(),
        notify=_on_shading_changed,
    )


@persistent
def _on_load(_dummy=None):
    _clarisse_settings(bpy.context.scene)
    _arm_airbag()
    _force_rendered()
    _subscribe()  # msgbus saute au chargement de fichier, on se réabonne


# ---------------------------------------------------------------------------
# Désarmement du pie menu Z (et Shift+Z) dans le keymap
# ---------------------------------------------------------------------------
_disabled_keymap_items = []


def _disarm_z():
    kc = bpy.context.window_manager.keyconfigs.user
    km = kc.keymaps.get("3D View")
    if not km:
        return
    for kmi in km.keymap_items:
        if kmi.type == "Z" and kmi.idname in (
            "wm.call_menu_pie",      # Z → pie menu shading
            "view3d.toggle_shading", # Shift+Z / Z direct selon la config
        ):
            if kmi.active:
                kmi.active = False
                _disabled_keymap_items.append((km.name, kmi.id))


def _rearm_z():
    kc = bpy.context.window_manager.keyconfigs.user
    for km_name, kmi_id in _disabled_keymap_items:
        km = kc.keymaps.get(km_name)
        if km:
            for kmi in km.keymap_items:
                if kmi.id == kmi_id:
                    kmi.active = True
    _disabled_keymap_items.clear()


# ---------------------------------------------------------------------------
# UI : petit panneau N pour sortir du mode en conscience
# ---------------------------------------------------------------------------
class RENDERLOCK_OT_solid_escape(bpy.types.Operator):
    """Passer en Solid en sécurité (objets lourds affichés en bounds)"""
    bl_idname = "renderlock.solid_escape"
    bl_label = "Solid (sécurisé)"

    def execute(self, context):
        n = _arm_airbag()
        context.space_data.shading.type = "SOLID"
        self.report({"INFO"}, f"Solid sécurisé — {n} objets lourds passés en Bounds")
        return {"FINISHED"}


class RENDERLOCK_OT_back_to_rendered(bpy.types.Operator):
    """Revenir au mode Rendered"""
    bl_idname = "renderlock.back_to_rendered"
    bl_label = "Rendered"

    def execute(self, context):
        context.space_data.shading.type = "RENDERED"
        return {"FINISHED"}


class RENDERLOCK_PT_panel(bpy.types.Panel):
    bl_label = "Render Lock"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Render Lock"

    def draw(self, context):
        col = self.layout.column(align=True)
        col.operator("renderlock.back_to_rendered", icon="SHADING_RENDERED")
        col.operator("renderlock.solid_escape", icon="SHADING_SOLID")
        col.separator()
        col.label(text=f"Mode garde : {GUARD_MODE}")


classes = (RENDERLOCK_OT_solid_escape, RENDERLOCK_OT_back_to_rendered, RENDERLOCK_PT_panel)


def register():
    for c in classes:
        bpy.utils.register_class(c)
    bpy.app.handlers.load_post.append(_on_load)
    _disarm_z()
    # armement immédiat si on active l'addon sur un fichier déjà ouvert
    bpy.app.timers.register(lambda: (_on_load(), None)[1], first_interval=0.5)


def unregister():
    bpy.msgbus.clear_by_owner(_msgbus_owner)
    _rearm_z()
    if _on_load in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(_on_load)
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
