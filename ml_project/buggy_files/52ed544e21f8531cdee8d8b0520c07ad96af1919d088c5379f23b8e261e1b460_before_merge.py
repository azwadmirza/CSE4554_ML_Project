    async def cors_startup(app):
        """Initialize cors when app starts up."""
        cors_added = set()

        for route in list(app.router.routes()):
            if hasattr(route, 'resource'):
                route = route.resource
            if route in cors_added:
                continue
            cors.add(route)
            cors_added.add(route)