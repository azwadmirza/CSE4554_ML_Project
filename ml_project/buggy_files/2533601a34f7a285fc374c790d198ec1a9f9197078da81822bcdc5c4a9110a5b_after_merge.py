def _make_request_event_processor(aws_event, aws_context, configured_timeout):
    # type: (Any, Any, Any) -> EventProcessor
    start_time = datetime.utcnow()

    def event_processor(sentry_event, hint, start_time=start_time):
        # type: (Event, Hint, datetime) -> Optional[Event]
        remaining_time_in_milis = aws_context.get_remaining_time_in_millis()
        exec_duration = configured_timeout - remaining_time_in_milis

        extra = sentry_event.setdefault("extra", {})
        extra["lambda"] = {
            "function_name": aws_context.function_name,
            "function_version": aws_context.function_version,
            "invoked_function_arn": aws_context.invoked_function_arn,
            "aws_request_id": aws_context.aws_request_id,
            "execution_duration_in_millis": exec_duration,
            "remaining_time_in_millis": remaining_time_in_milis,
        }

        extra["cloudwatch logs"] = {
            "url": _get_cloudwatch_logs_url(aws_context, start_time),
            "log_group": aws_context.log_group_name,
            "log_stream": aws_context.log_stream_name,
        }

        request = sentry_event.get("request", {})

        if "httpMethod" in aws_event:
            request["method"] = aws_event["httpMethod"]

        request["url"] = _get_url(aws_event, aws_context)

        if "queryStringParameters" in aws_event:
            request["query_string"] = aws_event["queryStringParameters"]

        if "headers" in aws_event:
            request["headers"] = _filter_headers(aws_event["headers"])

        if _should_send_default_pii():
            user_info = sentry_event.setdefault("user", {})

            id = aws_event.get("identity", {}).get("userArn")
            if id is not None:
                user_info.setdefault("id", id)

            ip = aws_event.get("identity", {}).get("sourceIp")
            if ip is not None:
                user_info.setdefault("ip_address", ip)

            if "body" in aws_event:
                request["data"] = aws_event.get("body", "")
        else:
            if aws_event.get("body", None):
                # Unfortunately couldn't find a way to get structured body from AWS
                # event. Meaning every body is unstructured to us.
                request["data"] = AnnotatedValue("", {"rem": [["!raw", "x", 0, 0]]})

        sentry_event["request"] = request

        return sentry_event

    return event_processor