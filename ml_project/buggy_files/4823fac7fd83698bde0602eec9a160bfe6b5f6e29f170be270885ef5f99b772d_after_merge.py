    def __init__(self, config=None, args=None, timeout=7, return_to_browser=False):
        # Store the arg/config
        self.args = args
        self.config = config

        # Client mode:
        self.set_mode()

        # Return to browser or exit
        self.return_to_browser = return_to_browser

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
            self.log_and_exit("Client couldn't create socket {0}: {1}".format(uri, e))