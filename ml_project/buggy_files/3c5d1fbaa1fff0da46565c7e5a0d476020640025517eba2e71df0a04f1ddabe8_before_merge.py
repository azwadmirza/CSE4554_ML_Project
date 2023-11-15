def respond_with_json_bytes(
    request: Request, code: int, json_bytes: bytes, send_cors: bool = False,
):
    """Sends encoded JSON in response to the given request.

    Args:
        request: The http request to respond to.
        code: The HTTP response code.
        json_bytes: The json bytes to use as the response body.
        send_cors: Whether to send Cross-Origin Resource Sharing headers
            https://fetch.spec.whatwg.org/#http-cors-protocol

    Returns:
        twisted.web.server.NOT_DONE_YET if the request is still active.
    """

    request.setResponseCode(code)
    request.setHeader(b"Content-Type", b"application/json")
    request.setHeader(b"Content-Length", b"%d" % (len(json_bytes),))
    request.setHeader(b"Cache-Control", b"no-cache, no-store, must-revalidate")

    if send_cors:
        set_cors_headers(request)

    # note that this is zero-copy (the bytesio shares a copy-on-write buffer with
    # the original `bytes`).
    bytes_io = BytesIO(json_bytes)

    producer = NoRangeStaticProducer(request, bytes_io)
    producer.start()
    return NOT_DONE_YET