from . import callbacks, ops, previews, props, ui

modules = (
    callbacks,
    previews,
    props,
    ops,
    ui,
)


def register():
    for module in modules:
        module.register()


def unregister():
    for module in reversed(modules):
        module.unregister()
