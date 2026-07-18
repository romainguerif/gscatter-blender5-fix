from typing import Callable

import bpy

_callbacks = []


def add_callback(callback: Callable, *args, **kwargs):
    """Add a callback to run when context is available."""
    _callbacks.append((callback, args, kwargs))


def _timer():
    for callback, args, kwargs in _callbacks:
        callback(*args, **kwargs)


def register():
    if not bpy.app.timers.is_registered(_timer):
        bpy.app.timers.register(_timer)


def unregister():
    if bpy.app.timers.is_registered(_timer):
        bpy.app.timers.unregister(_timer)

    # Clear the list here or get double items next time.
    _callbacks.clear()
