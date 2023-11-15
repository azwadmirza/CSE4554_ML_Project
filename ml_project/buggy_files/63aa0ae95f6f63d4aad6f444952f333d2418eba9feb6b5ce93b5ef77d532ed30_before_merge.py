def _sentry_start_response(
    old_start_response, span, status, response_headers, exc_info=None
):
    # type: (Callable[[str, U, Optional[E]], T], Span, str, U, Optional[E]) -> T
    with capture_internal_exceptions():
        status_int = int(status.split(" ", 1)[0])
        span.set_http_status(status_int)

    return old_start_response(status, response_headers, exc_info)