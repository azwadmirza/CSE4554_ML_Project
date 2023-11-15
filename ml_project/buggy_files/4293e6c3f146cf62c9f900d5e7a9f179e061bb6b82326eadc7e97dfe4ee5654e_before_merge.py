    def __init__(self, core):
        super(MpdFrontend, self).__init__()
        hostname = network.format_hostname(settings.MPD_SERVER_HOSTNAME)
        port = settings.MPD_SERVER_PORT

        try:
            network.Server(
                hostname, port,
                protocol=session.MpdSession, protocol_kwargs={'core': core},
                max_connections=settings.MPD_SERVER_MAX_CONNECTIONS,
                timeout=settings.MPD_SERVER_CONNECTION_TIMEOUT)
        except IOError as error:
            logger.error(
                'MPD server startup failed: %s',
                encoding.locale_decode(error))
            sys.exit(1)

        logger.info('MPD server running at [%s]:%s', hostname, port)