    def render(self, request):
        """
        Render a request by forwarding it to the proxied server.

        Args:
            request (Request): Incoming request.

        Returns:
            not_done (char): Indicator to note request not yet finished.

        """
        # RFC 2616 tells us that we can omit the port if it's the default port,
        # but we have to provide it otherwise
        request.content.seek(0, 0)
        qs = urlparse.urlparse(request.uri)[4]
        if qs:
            rest = self.path + '?' + qs
        else:
            rest = self.path
        clientFactory = self.proxyClientFactoryClass(
            request.method, rest, request.clientproto,
            request.getAllHeaders(), request.content.read(), request)
        clientFactory.noisy = False
        self.reactor.connectTCP(self.host, self.port, clientFactory)
        # don't trigger traceback if connection is lost before request finish.
        request.notifyFinish().addErrback(lambda f: f.cancel())
        return NOT_DONE_YET