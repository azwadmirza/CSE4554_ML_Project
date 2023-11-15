def config_checks(
        config,
        _get_color_from_vdir=get_color_from_vdir,
        _get_vdir_type=get_vdir_type):
    """do some tests on the config we cannot do with configobj's validator"""
    if len(config['calendars'].keys()) < 1:
        logger.fatal('Found no calendar section in the config file')
        raise InvalidSettingsError()
    config['sqlite']['path'] = expand_db_path(config['sqlite']['path'])
    if not config['locale']['default_timezone']:
        config['locale']['default_timezone'] = is_timezone(
            config['locale']['default_timezone'])
    if not config['locale']['local_timezone']:
        config['locale']['local_timezone'] = is_timezone(
            config['locale']['local_timezone'])

    # expand calendars with type = discover
    vdirs_complete = list()
    vdir_colors_from_config = {}
    for calendar in list(config['calendars'].keys()):
        if not isinstance(config['calendars'][calendar], dict):
            logger.fatal('Invalid config file, probably missing calendar sections')
            raise InvalidSettingsError
        if config['calendars'][calendar]['type'] == 'discover':
            logger.debug(
                'discovering calendars in {}'.format(config['calendars'][calendar]['path'])
            )
            vdirs = get_all_vdirs(config['calendars'][calendar]['path'])
            vdirs_complete += vdirs
            if 'color' in config['calendars'][calendar]:
                for vdir in vdirs:
                    vdir_colors_from_config[vdir] = config['calendars'][calendar]['color']
            config['calendars'].pop(calendar)
    for vdir in sorted(vdirs_complete):
        calendar = {'path': vdir,
                    'color': _get_color_from_vdir(vdir),
                    'type': _get_vdir_type(vdir),
                    'readonly': False
                    }

        # get color from config if not defined in vdir

        if calendar['color'] is None and vdir in vdir_colors_from_config:
            logger.debug("using collection's color for {}".format(vdir))
            calendar['color'] = vdir_colors_from_config[vdir]

        name = get_unique_name(vdir, config['calendars'].keys())
        config['calendars'][name] = calendar

    test_default_calendar(config)
    for calendar in config['calendars']:
        if config['calendars'][calendar]['type'] == 'birthdays':
            config['calendars'][calendar]['readonly'] = True
        if config['calendars'][calendar]['color'] == 'auto':
            config['calendars'][calendar]['color'] = \
                _get_color_from_vdir(config['calendars'][calendar]['path'])