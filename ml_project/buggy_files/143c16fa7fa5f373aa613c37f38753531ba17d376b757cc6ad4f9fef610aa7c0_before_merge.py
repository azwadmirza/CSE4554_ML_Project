def _update_monospace_fonts():
    """Update all fonts if fonts.monospace was set."""
    configtypes.Font.monospace_fonts = config.val.fonts.monospace
    for name, opt in configdata.DATA.items():
        if name == 'fonts.monospace':
            continue
        elif not isinstance(opt.typ, configtypes.Font):
            continue
        elif not config.instance.get_obj(name).endswith(' monospace'):
            continue

        config.instance.changed.emit(name)