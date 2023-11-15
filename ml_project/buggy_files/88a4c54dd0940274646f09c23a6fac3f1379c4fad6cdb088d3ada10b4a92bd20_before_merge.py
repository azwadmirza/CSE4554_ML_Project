def set_presets(**kwargs):
    if 'presets' in kwargs:
        presets = kwargs['presets']
        if presets is None:
            return kwargs
        if not isinstance(presets, list):
            presets = [presets]
        preset_kwargs = {}
        for preset in presets:
            if isinstance(preset, str):
                preset_orig = preset
                preset = preset_dict.get(preset, None)
                if preset is None:
                    raise ValueError(f'Preset \'{preset_orig}\' was not found. Valid presets: {list(preset_dict.keys())}')
            if isinstance(preset, dict):
                for key in preset:
                    preset_kwargs[key] = preset[key]
            else:
                raise TypeError(f'Preset of type {type(preset)} was given, but only presets of type [dict, str] are valid.')
        for key in preset_kwargs:
            if key not in kwargs:
                kwargs[key] = preset_kwargs[key]
    return kwargs