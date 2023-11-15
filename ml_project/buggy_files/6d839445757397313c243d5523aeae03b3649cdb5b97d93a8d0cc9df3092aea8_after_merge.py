def _get_url(aws_event, aws_context):
    # type: (Any, Any) -> str
    path = aws_event.get("path", None)
    headers = aws_event.get("headers", {})
    host = headers.get("Host", None)
    proto = headers.get("X-Forwarded-Proto", None)
    if proto and host and path:
        return "{}://{}{}".format(proto, host, path)
    return "awslambda:///{}".format(aws_context.function_name)