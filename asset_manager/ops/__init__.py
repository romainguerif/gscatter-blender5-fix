from . import install, misc, page, popup, scatter

modules = (
    misc,
    page,
    scatter,
    install,
    popup,
)


def register():
    for module in modules:
        module.register()


def unregister():
    for module in reversed(modules):
        module.unregister()
