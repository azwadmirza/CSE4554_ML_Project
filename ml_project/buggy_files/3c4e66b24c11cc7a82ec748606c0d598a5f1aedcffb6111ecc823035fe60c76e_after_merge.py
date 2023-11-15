    def check_origin(self, origin):
        ''' Implement a check_origin policy for Tornado to call.

        The suplied origin will be compared to the Bokeh server whitelist. If the
        origin is not allow, an error will be logged and ``False`` will be returned.

        Args:
            origin (str) :
                The URL of the connection origin

        Returns:
            bool, True if the connection is allowed, False otherwise

        '''
        from ..util import check_whitelist
        parsed_origin = urlparse(origin)
        origin_host = parsed_origin.netloc.lower()

        allowed_hosts = self.application.websocket_origins

        allowed = check_whitelist(origin_host, allowed_hosts)
        if allowed:
            return True
        else:
            log.error("Refusing websocket connection from Origin '%s'; \
                      use --allow-websocket-origin=%s to permit this; currently we allow origins %r",
                      origin, origin_host, allowed_hosts)
            return False