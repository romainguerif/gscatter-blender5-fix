from . import effect_layers, effect_manager, optimization

modules = (
    effect_layers,
    optimization,
    effect_manager,
)


def register():
    for module in modules:
        module.register()


def unregister():
    for module in reversed(modules):
        module.unregister()
