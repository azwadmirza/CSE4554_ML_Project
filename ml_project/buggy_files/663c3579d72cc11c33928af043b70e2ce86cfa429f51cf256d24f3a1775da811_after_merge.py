    def handle_channels(
        self,
        channels: List[InputChannel],
        http_port: int = constants.DEFAULT_SERVER_PORT,
        route: Text = "/webhooks/",
        cors: Union[Text, List[Text], None] = None,
    ) -> Sanic:
        """Start a webserver attaching the input channels and handling msgs."""

        from rasa.core import run

        logger.warning(
            "DEPRECATION warning: Using `handle_channels` is deprecated. "
            "Please use `rasa.run(...)` or see "
            "`rasa.core.run.configure_app(...)` if you want to implement "
            "this on a more detailed level."
        )

        app = run.configure_app(channels, cors, None, enable_api=False, route=route)

        app.agent = self

        update_sanic_log_level()

        app.run(
            host="0.0.0.0",
            port=http_port,
            backlog=int(os.environ.get("SANIC_BACKLOG", "100")),
        )

        # this might seem unnecessary (as run does not return until the server
        # is killed) - but we use it for tests where we mock `.run` to directly
        # return and need the app to inspect if we created a properly
        # configured server
        return app