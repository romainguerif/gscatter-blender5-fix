from . import props, scopped_slow_task

modules = (
    props,
    scopped_slow_task,
)


def register():
    for module in modules:
        module.register()


def unregister():
    for module in reversed(modules):
        module.unregister()
