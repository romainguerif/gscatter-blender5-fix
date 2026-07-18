from . import props, callbacks, ops, ui, store

modules = (props, ops, ui, callbacks, store)


def register():
    for module in modules:
        module.register()


def unregister():
    for module in reversed(modules):
        module.unregister()
