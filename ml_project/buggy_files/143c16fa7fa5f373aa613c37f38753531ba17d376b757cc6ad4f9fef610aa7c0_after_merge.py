def _update_monospace_fonts():
    """Update all fonts if fonts.monospace was set."""
    configtypes.Font.monospace_fonts = config.val.fonts.monospace
    for name, opt in configdata.DATA.items():
        if name == 'fonts.monospace':
            continue
        elif not isinstance(opt.typ, configtypes.Font):
            continue

        value = config.instance.get_obj(name)
        if value is None or not value.endswith(' monospace'):
            continue

        config.instance.changed.emit(name)