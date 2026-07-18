from typing import TYPE_CHECKING

from bpy.types import Context

from ..utils.getters import get_wm_props

if TYPE_CHECKING:
    from .props import IconViewerWidget


def get_icon_viewer_props(source: Context = None) -> "IconViewerWidget":
    return get_wm_props(source).icon_viewer
