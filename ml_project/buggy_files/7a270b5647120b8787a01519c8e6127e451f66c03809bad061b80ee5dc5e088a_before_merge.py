def validate_extension(extension):
    """Verify extension's dependencies and environment.

    :param extensions: an extension to check
    :returns: if extension should be run
    """

    logger.debug('Validating extension: %s', extension.ext_name)

    if extension.ext_name != extension.entry_point.name:
        logger.warning(
            'Disabled extension %(ep)s: entry point name (%(ep)s) '
            'does not match extension name (%(ext)s)',
            {'ep': extension.entry_point.name, 'ext': extension.ext_name})
        return False

    try:
        extension.entry_point.require()
    except pkg_resources.DistributionNotFound as ex:
        logger.info(
            'Disabled extension %s: Dependency %s not found',
            extension.ext_name, ex)
        return False
    except pkg_resources.VersionConflict as ex:
        found, required = ex.args
        logger.info(
            'Disabled extension %s: %s required, but found %s at %s',
            extension.ext_name, required, found, found.location)
        return False

    try:
        extension.validate_environment()
    except exceptions.ExtensionError as ex:
        logger.info(
            'Disabled extension %s: %s', extension.ext_name, ex.message)
        return False

    return True