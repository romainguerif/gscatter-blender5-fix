from typing import TYPE_CHECKING
import bpy
from bpy.app.handlers import persistent
from ..utils.getters import get_node_tree
from . import default
from uuid import uuid4

if TYPE_CHECKING:
    from ..effects.props import EffectLayerProps


@persistent
def effect_instance_id_handler(self, context: bpy.types.Context):
    """Handler to check effect instance ids"""
    for obj in bpy.data.objects:
        node_tree = get_node_tree(obj)
        if node_tree is None:
            continue
        for category in default.EFFECT_CATEGORIES:
            node: bpy.types.GeometryNodeGroup = node_tree.nodes[category]
            effects: list[EffectLayerProps] = node.node_tree.gscatter.effects
            for effect in effects:
                if effect.instance_id == "":
                    effect.instance_id = str(uuid4())


def register():
    bpy.app.handlers.load_post.append(effect_instance_id_handler)


def unregister():
    pass
