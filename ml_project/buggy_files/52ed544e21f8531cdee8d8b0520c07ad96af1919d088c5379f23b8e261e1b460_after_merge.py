    async def cors_startup(app):
        """Initialize cors when app starts up."""
        for route in list(app.router.routes()):
            _allow_cors(route)