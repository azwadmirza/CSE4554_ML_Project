def global_options(f):
    def config_callback(ctx, option, config):
        prepare_context(ctx, config)

    def verbosity_callback(ctx, option, verbose):
        if verbose:
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)

    config = click.option('--config', '-c', default=None, metavar='PATH',
                          help='The config file to use.', is_eager=True,
                          expose_value=False, callback=config_callback)
    verbose = click.option('--verbose', '-v', is_flag=True,
                           help='Output debugging information.',
                           expose_value=False,
                           callback=verbosity_callback)
    version = click.version_option(version=__version__)

    return config(verbose(version(f)))