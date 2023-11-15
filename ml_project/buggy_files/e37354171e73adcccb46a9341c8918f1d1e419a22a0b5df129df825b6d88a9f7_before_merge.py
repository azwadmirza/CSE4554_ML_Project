def _capture_exception():
    hub = Hub.current
    exc_info = sys.exc_info()

    if hub.get_integration(CeleryIntegration) is not None:
        event, hint = event_from_exception(
            exc_info,
            client_options=hub.client.options,
            mechanism={"type": "celery", "handled": False},
        )
        hub.capture_event(event, hint=hint)

    return exc_info