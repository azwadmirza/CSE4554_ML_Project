def _get_library(args, config):
    libraries = dict((l.name, l) for l in args.registry['local:library'])
    library_name = config['local']['library']

    if library_name not in libraries:
        logger.error('Local library %s not found', library_name)
        return None

    logger.debug('Using %s as the local library', library_name)
    return libraries[library_name](config)