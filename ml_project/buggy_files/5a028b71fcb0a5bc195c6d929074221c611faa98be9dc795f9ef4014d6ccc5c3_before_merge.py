async def respond_with_responder(
    request, responder, media_type, file_size, upload_name=None
):
    """Responds to the request with given responder. If responder is None then
    returns 404.

    Args:
        request (twisted.web.http.Request)
        responder (Responder|None)
        media_type (str): The media/content type.
        file_size (int|None): Size in bytes of the media. If not known it should be None
        upload_name (str|None): The name of the requested file, if any.
    """
    if not responder:
        respond_404(request)
        return

    logger.debug("Responding to media request with responder %s", responder)
    add_file_headers(request, media_type, file_size, upload_name)
    try:
        with responder:
            await responder.write_to_consumer(request)
    except Exception as e:
        # The majority of the time this will be due to the client having gone
        # away. Unfortunately, Twisted simply throws a generic exception at us
        # in that case.
        logger.warning("Failed to write to consumer: %s %s", type(e), e)

        # Unregister the producer, if it has one, so Twisted doesn't complain
        if request.producer:
            request.unregisterProducer()

    finish_request(request)