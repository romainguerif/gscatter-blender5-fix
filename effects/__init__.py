from . import callbacks, ops, props, ui, store

modules = (callbacks, props, ops, ui, store)


def register():
    for module in modules:
        module.register()


def unregister():
    for module in reversed(modules):
        module.unregister()
