    def __init__(self, core):
        super(MpdFrontend, self).__init__()
        hostname = network.format_hostname(settings.MPD_SERVER_HOSTNAME)
        port = settings.MPD_SERVER_PORT

        # NOTE kwargs dict keys must be bytestrings to work on Python < 2.6.5
        # See https://github.com/mopidy/mopidy/issues/302 for details.
        try:
            network.Server(
                hostname, port,
                protocol=session.MpdSession, protocol_kwargs={b'core': core},
                max_connections=settings.MPD_SERVER_MAX_CONNECTIONS,
                timeout=settings.MPD_SERVER_CONNECTION_TIMEOUT)
        except IOError as error:
            logger.error(
                'MPD server startup failed: %s',
                encoding.locale_decode(error))
            sys.exit(1)

        logger.info('MPD server running at [%s]:%s', hostname, port)