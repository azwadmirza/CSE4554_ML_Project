    def sentry_handler(aws_event, context, *args, **kwargs):
        # type: (Any, Any, *Any, **Any) -> Any

        # Per https://docs.aws.amazon.com/lambda/latest/dg/python-handler.html,
        # `event` here is *likely* a dictionary, but also might be a number of
        # other types (str, int, float, None).
        #
        # In some cases, it is a list (if the user is batch-invoking their
        # function, for example), in which case we'll use the first entry as a
        # representative from which to try pulling request data. (Presumably it
        # will be the same for all events in the list, since they're all hitting
        # the lambda in the same request.)

        if isinstance(aws_event, list):
            request_data = aws_event[0]
            batch_size = len(aws_event)
        else:
            request_data = aws_event
            batch_size = 1

        if not isinstance(request_data, dict):
            # If we're not dealing with a dictionary, we won't be able to get
            # headers, path, http method, etc in any case, so it's fine that
            # this is empty
            request_data = {}

        hub = Hub.current
        integration = hub.get_integration(AwsLambdaIntegration)
        if integration is None:
            return handler(aws_event, context, *args, **kwargs)

        # If an integration is there, a client has to be there.
        client = hub.client  # type: Any
        configured_time = context.get_remaining_time_in_millis()

        with hub.push_scope() as scope:
            with capture_internal_exceptions():
                scope.clear_breadcrumbs()
                scope.add_event_processor(
                    _make_request_event_processor(
                        request_data, context, configured_time
                    )
                )
                scope.set_tag("aws_region", context.invoked_function_arn.split(":")[3])
                if batch_size > 1:
                    scope.set_tag("batch_request", True)
                    scope.set_tag("batch_size", batch_size)

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

            headers = request_data.get("headers", {})
            transaction = Transaction.continue_from_headers(
                headers, op="serverless.function", name=context.function_name
            )
            with hub.start_transaction(transaction):
                try:
                    return handler(aws_event, context, *args, **kwargs)
                except Exception:
                    exc_info = sys.exc_info()
                    sentry_event, hint = event_from_exception(
                        exc_info,
                        client_options=client.options,
                        mechanism={"type": "aws_lambda", "handled": False},
                    )
                    hub.capture_event(sentry_event, hint=hint)
                    reraise(*exc_info)
                finally:
                    if timeout_thread:
                        timeout_thread.stop()