from . import props, callbacks, ops, ui

modules = (props, callbacks, ops, ui)


def register():
    for module in modules:
        module.register()


def unregister():
    for module in reversed(modules):
        module.unregister()
