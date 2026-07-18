import bpy

from ..utils.logger import debug

from ..utils.getters import get_preferences


def open_window(ui_type: str):
    prefs = get_preferences()
    window = bpy.context.window
    current_screen = bpy.context.screen
    new_area = None

    # Split the current layout area
    match prefs.asset_browser_window_size:
        case "small":
            assetbrowser_width = 0.25
        case "medium":
            assetbrowser_width = 0.42
        case "big":
            assetbrowser_width = 0.5
    factor = (
        assetbrowser_width * 2
        if prefs.asset_browser_dock_side == "left"
        or prefs.asset_browser_dock_side == "down"
        else 1
    )
    direction = (
        "HORIZONTAL"
        if prefs.asset_browser_dock_side == "down"
        or prefs.asset_browser_dock_side == "up"
        else "VERTICAL"
    )
    bpy.ops.screen.area_split(direction=direction, factor=factor - assetbrowser_width)

    # Get the newly created area (it will be the last area in the screen's areas list)
    new_area = current_screen.areas[-1]
    new_area.type = "FILE_BROWSER"

    # Change area type
    if not prefs.asset_browser_docked:
        # Save override before duplicating the area
        new_area_override = {
            "window": window,
            "screen": window.screen,
            "area": new_area,
            "region": new_area.regions[-1],
        }
        with bpy.context.temp_override(**new_area_override):
            # Popout layout as new window
            bpy.ops.screen.area_dupli("INVOKE_DEFAULT")

            window = bpy.context.window_manager.windows[-1]
            new_area = window.screen.areas[0]

    new_area.type = "FILE_BROWSER"
    new_area.ui_type = ui_type

    def defer():
        active_space = new_area.spaces.active
        params = active_space.params
        if not params:
            return 0

        if bpy.app.version >= (4, 2, 0):
            # Since paramter name changed
            params.asset_library_reference = "Graswald"
            active_space.show_region_toolbar = False
            active_space.show_region_tool_props = True
        else:
            params.asset_library_ref = "Graswald"
            active_space.show_region_toolbar = False
            active_space.show_region_tool_props = True

        # params = bpy.context.space_data.params
        filter_id = params.filter_asset_id
        setattr(filter_id, "filter_action", False)
        setattr(filter_id, "filter_node_tree", False)
        setattr(filter_id, "filter_world", False)
        # params.import_type = 'APPEND'

        if not prefs.asset_browser_docked:
            with bpy.context.temp_override(**new_area_override):
                # Close area below
                bpy.ops.screen.area_close("INVOKE_DEFAULT")

    bpy.app.timers.register(defer)
    return window


asset_browser_windows = []


def get_asset_browser_windows():
    global asset_browser_windows
    return asset_browser_windows


def refresh_library():
    for win in asset_browser_windows:
        screen = win.screen
        if screen is None:
            continue
        if getattr(screen, "areas") is None:
            continue
        for area in screen.areas:
            if area.ui_type != "ASSETS":
                continue
            if bpy.app.version >= (4, 2, 0):
                if area.spaces.active.params.asset_library_reference != "Graswald":
                    continue
            else:
                if area.spaces.active.params.asset_library_ref != "Graswald":
                    continue
            # Refresh the asset browser
            with bpy.context.temp_override(window=win, screen=screen, area=area):
                try:
                    params = bpy.context.area.spaces.active.params
                    if not params.asset_filter:
                        params.asset_filter = "ALL"
                    bpy.context.area.spaces.active.params.catalog_id = params.catalog_id
                    bpy.ops.asset.library_refresh()
                except Exception:
                    ...
                debug("Refresh Library")


def refresh_viewport():
    for win in asset_browser_windows:
        screen = win.screen
        for area in screen.areas:
            if area.ui_type != "ASSETS":
                continue
            try:
                if area.spaces.active.params.asset_library_ref != "Graswald":
                    continue
            except Exception:
                if area.spaces.active.params.asset_library_reference != "Graswald":
                    continue
            if area.ui_type == "VIEW_3D":
                area.tag_redraw()


def open_asset_browser(show_free_assets=False):
    global asset_browser_windows

    if len(asset_browser_windows) > 0:
        debug(f"Asset Browser Windows: {len(asset_browser_windows)}")
        is_open = False
        ab_area = None
        for win in bpy.context.window_manager.windows:
            screen = win.screen
            for area in screen.areas:
                if area.ui_type == "ASSETS":
                    active_space = area.spaces.active
                    params = active_space.params
                    library = getattr(
                        params,
                        "asset_library_reference",
                        getattr(params, "asset_library_ref"),
                    )
                    if library == "Graswald":
                        is_open = True
                        ab_area = area

        for win in asset_browser_windows:
            asset_browser_windows.remove(win)
            if is_open:
                if len(win.screen.areas) == 1:
                    area = ab_area
                    new_area_override = {
                        "window": win,
                        "screen": win.screen,
                        "area": area,
                        "region": area.regions[-1],
                    }
                    with bpy.context.temp_override(**new_area_override):
                        bpy.ops.wm.window_close("INVOKE_DEFAULT")
                if len(win.screen.areas) > 1:
                    area = ab_area
                    new_area_override = {
                        "window": win,
                        "screen": win.screen,
                        "area": area,
                        "region": area.regions[-1],
                    }
                    with bpy.context.temp_override(**new_area_override):
                        bpy.ops.screen.area_close("INVOKE_DEFAULT")
        if not is_open:
            window = open_window("ASSETS")
            asset_browser_windows.append(window)
    else:
        window = open_window("ASSETS")
        asset_browser_windows.append(window)


def set_catalog_id(id):
    for win in asset_browser_windows:
        screen = win.screen
        for area in win.screen.areas:
            if area.ui_type != "ASSETS":
                continue
            try:
                if area.spaces.active.params.asset_library_ref != "Graswald":
                    continue
            except Exception:
                if area.spaces.active.params.asset_library_reference != "Graswald":
                    continue
            with bpy.context.temp_override(window=win, screen=screen, area=area):
                params = bpy.context.area.spaces.active.params
                try:
                    params.catalog_id = id
                except Exception:
                    ...
