def _get_url(event, context):
    # type: (Any, Any) -> str
    path = event.get("path", None)
    headers = event.get("headers", {})
    host = headers.get("Host", None)
    proto = headers.get("X-Forwarded-Proto", None)
    if proto and host and path:
        return "{}://{}{}".format(proto, host, path)
    return "awslambda:///{}".format(context.function_name)