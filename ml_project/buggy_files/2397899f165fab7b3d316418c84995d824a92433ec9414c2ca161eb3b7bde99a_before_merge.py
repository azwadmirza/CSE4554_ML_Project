    def setup_connection(self):
        # on *NIX, the proxy can show up either upper or lowercase.
        # Prefer lower case, and prefer HTTPS over HTTP if the urlscheme
        # is https.
        proxy = os.environ.get(
            'http_proxy', os.environ.get(
                'HTTP_PROXY', ''))
        if urlscheme == 'https':
            proxy = os.environ.get(
                'https_proxy', os.environ.get(
                    'HTTPS_PROXY', proxy))
        if proxy:
            p = ProxiedTransport()
            p.set_proxy(proxy)
            self.neos = xmlrpclib.ServerProxy(urlscheme+"://www.neos-server.org:"+port,transport=p)
        else:
            self.neos = xmlrpclib.ServerProxy(urlscheme+"://www.neos-server.org:"+port)
        logger.info("Connecting to the NEOS server ... ")
        try:
            result = self.neos.ping()
            logger.info("OK.")
        except socket.error:
            e = sys.exc_info()[1]
            self.neos = None
            logger.info("Fail.")
            logger.warning("NEOS is temporarily unavailable.\n")