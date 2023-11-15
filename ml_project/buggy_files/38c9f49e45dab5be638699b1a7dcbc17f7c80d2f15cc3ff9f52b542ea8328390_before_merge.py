def get_config(config_path=None):
    """reads the config file, validates it and return a config dict

    :param config_path: path to a custom config file, if none is given the
                        default locations will be searched
    :type config_path: str
    :returns: configuration
    :rtype: dict
    """
    if config_path is None:
        config_path = _find_configuration_file()

    logger.debug('using the config file at {}'.format(config_path))
    config = ConfigObj(DEFAULTSPATH, interpolation=False)

    try:
        user_config = ConfigObj(config_path,
                                configspec=SPECPATH,
                                interpolation=False,
                                file_error=True,
                                )
    except ConfigObjError as error:
        logger.fatal('parsing the config file file with the following error: '
                     '{}'.format(error))
        logger.fatal('if you recently updated khal, the config file format '
                     'might have changed, in that case please consult the '
                     'CHANGELOG or other documentation')
        sys.exit(1)

    fdict = {'timezone': is_timezone,
             'expand_path': expand_path,
             }
    validator = Validator(fdict)
    results = user_config.validate(validator, preserve_errors=True)
    if not results:
        for entry in flatten_errors(config, results):
            # each entry is a tuple
            section_list, key, error = entry
            if key is not None:
                section_list.append(key)
            else:
                section_list.append('[missing section]')
            section_string = ', '.join(section_list)
            if error is False:
                error = 'Missing value or section.'
            print(section_string, ' = ', error)
        raise ValueError  # TODO own error class

    config.merge(user_config)
    config_checks(config)

    extras = get_extra_values(user_config)
    for section, value in extras:
        if section == ():
            logger.warn('unknown section "{}" in config file'.format(value))
        else:
            section = sectionize(section)
            logger.warn('unknown key or subsection "{}" in '
                        'section "{}"'.format(value, section))
    return config