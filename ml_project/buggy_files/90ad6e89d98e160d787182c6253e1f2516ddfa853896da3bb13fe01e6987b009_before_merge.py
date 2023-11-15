    def __init__(self, config, core):
        super(MpdFrontend, self).__init__()
        hostname = network.format_hostname(config['mpd']['hostname'])
        port = config['mpd']['port']

        # NOTE kwargs dict keys must be bytestrings to work on Python < 2.6.5
        # See https://github.com/mopidy/mopidy/issues/302 for details.
        try:
            network.Server(
                hostname, port,
                protocol=session.MpdSession,
                protocol_kwargs={
                    b'config': config,
                    b'core': core,
                },
                max_connections=config['mpd']['max_connections'],
                timeout=config['mpd']['connection_timeout'])
        except IOError as error:
            logger.error(
                'MPD server startup failed: %s',
                encoding.locale_decode(error))
            sys.exit(1)

        logger.info('MPD server running at [%s]:%s', hostname, port)