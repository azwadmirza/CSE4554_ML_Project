def global_options(f):
    config = click.option('--config', '-c', default=None, metavar='PATH',
                          help='The config file to use.')
    verbose = click.option('--verbose', '-v', is_flag=True,
                           help='Output debugging information.')
    version = click.version_option(version=__version__)

    return config(verbose(version(f)))