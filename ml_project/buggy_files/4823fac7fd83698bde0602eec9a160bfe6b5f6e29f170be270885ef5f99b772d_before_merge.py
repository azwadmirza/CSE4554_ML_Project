    def __init__(self, config=None, args=None, timeout=7, return_to_browser=False):
        # Store the arg/config
        self.args = args
        self.config = config

        # Client mode:
        self.set_mode()

        # Build the URI
        if args.password != "":
            uri = 'http://{0}:{1}@{2}:{3}'.format(args.username, args.password,
                                                  args.client, args.port)
        else:
            uri = 'http://{0}:{1}'.format(args.client, args.port)
        logger.debug("Try to connect to {0}".format(uri))

        # Try to connect to the URI
        transport = GlancesClientTransport()
        # Configure the server timeout
        transport.set_timeout(timeout)
        try:
            self.client = ServerProxy(uri, transport=transport)
        except Exception as e:
            msg = "Client couldn't create socket {0}: {1}".format(uri, e)
            if not return_to_browser:
                logger.critical(msg)
                sys.exit(2)
            else:
                logger.error(msg)