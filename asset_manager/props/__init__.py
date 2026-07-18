from . import (
    environment,
    asset,
    product,
    asset_configurator,
    author,
    base,
    free_assets,
    library,
    library_configurator,
    previews,
    tag,
)

modules = (
    base,
    author,
    previews,
    asset_configurator,
    asset,
    product,
    environment,
    tag,
    library_configurator,
    free_assets,
    library,
)


def register():
    for module in modules:
        module.register()


def unregister():
    for module in reversed(modules):
        module.unregister()
