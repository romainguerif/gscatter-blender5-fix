from . import scatter_system_preset_store

scattersystempresetstore = scatter_system_preset_store.ScatterSystemPresetStore()


def register():
    pass


def unregister():
    scattersystempresetstore.store()
