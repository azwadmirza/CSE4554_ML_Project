def s3_open_key(key, mode, **kwargs):
    logger.debug('%r', locals())
    #
    # TODO: handle boto3 keys as well
    #
    host = kwargs.pop('host', None)
    if host is not None:
        kwargs['endpoint_url'] = 'http://' + host

    if kwargs.pop("ignore_extension", False):
        codec = None
    else:
        codec = _detect_codec(key.name)

    #
    # Codecs work on a byte-level, so the underlying S3 object should
    # always be reading bytes.
    #
    if codec and mode in (smart_open_s3.READ, smart_open_s3.READ_BINARY):
        s3_mode = smart_open_s3.READ_BINARY
    elif codec and mode in (smart_open_s3.WRITE, smart_open_s3.WRITE_BINARY):
        s3_mode = smart_open_s3.WRITE_BINARY
    else:
        s3_mode = mode

    logging.debug('codec: %r mode: %r s3_mode: %r', codec, mode, s3_mode)
    fobj = smart_open_s3.open(key.bucket.name, key.name, s3_mode, **kwargs)
    return _CODECS[codec](fobj, mode)