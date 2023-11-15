    def getChild(self, path, request):
        """
        Create and return a proxy resource with the same proxy configuration
        as this one, except that its path also contains the segment given by
        path at the end.

        Args:
            path (str): Url path.
            request (Request object): Incoming request.

        Return:
            resource (EvenniaReverseProxyResource): A proxy resource.

        """
        request.notifyFinish().addErrback(lambda f: logger.log_trace("%s\nCaught errback in webserver.py:75." % f))
        return EvenniaReverseProxyResource(
            self.host, self.port, self.path + '/' + urlquote(path, safe=""),
            self.reactor)