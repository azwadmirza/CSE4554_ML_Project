    def startProxyConnect(self):
        """
        Connect to explicit proxy.
        """
        # construct proxy connect HTTP request
        #
        request = "CONNECT %s:%d HTTP/1.1\x0d\x0a" % (self.factory.host.encode("utf-8"), self.factory.port)
        request += "Host: %s:%d\x0d\x0a" % (self.factory.host.encode("utf-8"), self.factory.port)
        request += "\x0d\x0a"

        self.log.debug("{request}", request=request)

        self.sendData(request)