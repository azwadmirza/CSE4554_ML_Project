def _wrap_init_error(init_error):
    # type: (F) -> F
    def sentry_init_error(*args, **kwargs):
        # type: (*Any, **Any) -> Any

        hub = Hub.current
        integration = hub.get_integration(AwsLambdaIntegration)
        if integration is None:
            return init_error(*args, **kwargs)

        # If an integration is there, a client has to be there.
        client = hub.client  # type: Any

        with capture_internal_exceptions():
            with hub.configure_scope() as scope:
                scope.clear_breadcrumbs()

            exc_info = sys.exc_info()
            if exc_info and all(exc_info):
                event, hint = event_from_exception(
                    exc_info,
                    client_options=client.options,
                    mechanism={"type": "aws_lambda", "handled": False},
                )
                hub.capture_event(event, hint=hint)

        return init_error(*args, **kwargs)

    return sentry_init_error  # type: ignore