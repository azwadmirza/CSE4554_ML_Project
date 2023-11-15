def read_configuration(
        filepath, find_others=False, ignore_option_errors=False):
    """Read given configuration file and returns options from it as a dict.

    :param str|unicode filepath: Path to configuration file
        to get options from.

    :param bool find_others: Whether to search for other configuration files
        which could be on in various places.

    :param bool ignore_option_errors: Whether to silently ignore
        options, values of which could not be resolved (e.g. due to exceptions
        in directives such as file:, attr:, etc.).
        If False exceptions are propagated as expected.

    :rtype: dict
    """
    from pex.third_party.setuptools.dist import Distribution, _Distribution

    filepath = os.path.abspath(filepath)

    if not os.path.isfile(filepath):
        raise DistutilsFileError(
            'Configuration file %s does not exist.' % filepath)

    current_directory = os.getcwd()
    os.chdir(os.path.dirname(filepath))

    try:
        dist = Distribution()

        filenames = dist.find_config_files() if find_others else []
        if filepath not in filenames:
            filenames.append(filepath)

        _Distribution.parse_config_files(dist, filenames=filenames)

        handlers = parse_configuration(
            dist, dist.command_options,
            ignore_option_errors=ignore_option_errors)

    finally:
        os.chdir(current_directory)

    return configuration_to_dict(handlers)