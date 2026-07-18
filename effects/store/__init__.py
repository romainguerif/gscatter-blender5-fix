from . import effect_store, effect_preset_store

effectstore = effect_store.EffectStore()
effectpresetstore = effect_preset_store.EffectPresetStore()


def register():
    pass


def unregister():
    effectstore.store()
    effectpresetstore.store()
