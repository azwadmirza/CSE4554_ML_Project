def stream_decode_response_unicode(iterator, r):
    """Stream decodes a iterator."""
    encoding = r.encoding

    if encoding is None:
        encoding = r.apparent_encoding

    try:
        decoder = codecs.getincrementaldecoder(encoding)(errors='replace')
    except (LookupError, TypeError):
        # A LookupError is raised if the encoding was not found which could
        # indicate a misspelling or similar mistake.
        #
        # A TypeError can be raised if encoding is None
        raise UnicodeError("Unable to decode contents with encoding %s." % encoding)

    for chunk in iterator:
        rv = decoder.decode(chunk)
        if rv:
            yield rv
    rv = decoder.decode(b'', final=True)
    if rv:
        yield rv