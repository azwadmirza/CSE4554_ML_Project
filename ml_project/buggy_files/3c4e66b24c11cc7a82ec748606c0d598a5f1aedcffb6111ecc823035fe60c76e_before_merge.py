    def check_origin(self, origin):
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