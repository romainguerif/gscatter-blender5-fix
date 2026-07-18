#  * Copyright (C) 2024 Graswald GmbH - All Rights Reserved
#  * You may use, distribute and modify this code under the
#  * terms of the GPLv3 license.
#  *
#  * You should have received a copy of the GPLv3 license with
#  * this file. If not, please write to: support@graswald3d.com, or visit https://gscatter.com/:
#  *

bl_info = {
    "name": "GScatter by Graswald",
    "description": "The Graswald Scattering Tools",
    "location": "View3D > Sidebar > GScatter & Geo-Nodes > Sidebar > GScatter",
    "author": "Graswald",
    "version": (0, 12, 0),
    "blender": (3, 5, 0),
    "support": "COMMUNITY",
    "category": "",
}

from . import (
    asset_manager,
    common,
    slow_task_manager,
    effects,
    environment,
    icon_viewer,
    icons,
    info,
    extras,
    scatter,
    utils,
)

modules = (
    common,
    slow_task_manager,
    icons,
    scatter,
    icon_viewer,
    asset_manager,
    effects,
    utils,
    environment,
    extras,
    info,
)


def register():
    for module in modules:
        module.register()


def unregister():
    for module in reversed(modules):
        module.unregister()
