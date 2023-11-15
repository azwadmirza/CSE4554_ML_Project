    def register(self, app, router):
        """Register the view with a router."""
        assert self.url is not None, 'No url set for view'
        urls = [self.url] + self.extra_urls
        routes = []

        for method in ('get', 'post', 'delete', 'put'):
            handler = getattr(self, method, None)

            if not handler:
                continue

            handler = request_handler_factory(self, handler)

            for url in urls:
                routes.append(router.add_route(method, url, handler))

        if not self.cors_allowed:
            return

        for route in routes:
            app['allow_cors'](route)