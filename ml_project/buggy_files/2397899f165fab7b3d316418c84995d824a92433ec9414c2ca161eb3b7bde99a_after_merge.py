    def setup_connection(self):
        # on *NIX, the proxy can show up either upper or lowercase.
        # Prefer lower case, and prefer HTTPS over HTTP if the
        # NEOS.scheme is https.
        proxy = os.environ.get(
            'http_proxy', os.environ.get(
                'HTTP_PROXY', ''))
        if NEOS.scheme == 'https':
            proxy = os.environ.get(
                'https_proxy', os.environ.get(
                    'HTTPS_PROXY', proxy))
        transport = None
        if proxy:
            transport = ProxiedTransport()
            transport.set_proxy(proxy)

        self.neos = xmlrpclib.ServerProxy(
            "%s://%s:%s" % (NEOS.scheme, NEOS.host, NEOS.port),
            transport=transport)

        logger.info("Connecting to the NEOS server ... ")
        try:
            result = self.neos.ping()
            logger.info("OK.")
        except socket.error:
            e = sys.exc_info()[1]
            self.neos = None
            logger.info("Fail.")
            logger.warning("NEOS is temporarily unavailable.\n")