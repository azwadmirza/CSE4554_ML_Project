    def sentry_handler(event, context, *args, **kwargs):
        # type: (Any, Any, *Any, **Any) -> Any
        hub = Hub.current
        integration = hub.get_integration(AwsLambdaIntegration)
        if integration is None:
            return handler(event, context, *args, **kwargs)

        # If an integration is there, a client has to be there.
        client = hub.client  # type: Any
        configured_time = context.get_remaining_time_in_millis()

        with hub.push_scope() as scope:
            with capture_internal_exceptions():
                scope.clear_breadcrumbs()
                scope.add_event_processor(
                    _make_request_event_processor(event, context, configured_time)
                )
                scope.set_tag("aws_region", context.invoked_function_arn.split(":")[3])

                timeout_thread = None
                # Starting the Timeout thread only if the configured time is greater than Timeout warning
                # buffer and timeout_warning parameter is set True.
                if (
                    integration.timeout_warning
                    and configured_time > TIMEOUT_WARNING_BUFFER
                ):
                    waiting_time = (
                        configured_time - TIMEOUT_WARNING_BUFFER
                    ) / MILLIS_TO_SECONDS

                    timeout_thread = TimeoutThread(
                        waiting_time,
                        configured_time / MILLIS_TO_SECONDS,
                    )

                    # Starting the thread to raise timeout warning exception
                    timeout_thread.start()

            headers = event.get("headers", {})
            transaction = Transaction.continue_from_headers(
                headers, op="serverless.function", name=context.function_name
            )
            with hub.start_transaction(transaction):
                try:
                    return handler(event, context, *args, **kwargs)
                except Exception:
                    exc_info = sys.exc_info()
                    event, hint = event_from_exception(
                        exc_info,
                        client_options=client.options,
                        mechanism={"type": "aws_lambda", "handled": False},
                    )
                    hub.capture_event(event, hint=hint)
                    reraise(*exc_info)
                finally:
                    if timeout_thread:
                        timeout_thread.stop()