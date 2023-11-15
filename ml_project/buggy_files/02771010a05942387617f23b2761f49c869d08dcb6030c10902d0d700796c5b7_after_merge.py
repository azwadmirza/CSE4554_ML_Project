def s3_open_uri(parsed_uri, mode, **kwargs):
    logger.debug('%r', locals())
    if parsed_uri.access_id is not None:
        kwargs['aws_access_key_id'] = parsed_uri.access_id
    if parsed_uri.access_secret is not None:
        kwargs['aws_secret_access_key'] = parsed_uri.access_secret

    # Get an S3 host. It is required for sigv4 operations.
    host = kwargs.pop('host', None)
    if host is not None:
        kwargs['endpoint_url'] = 'http://' + host

    #
    # TODO: this is the wrong place to handle ignore_extension.
    # It should happen at the highest level in the smart_open function, because
    # it influences other file systems as well, not just S3.
    #
    if kwargs.pop("ignore_extension", False):
        codec = None
    else:
        codec = _detect_codec(parsed_uri.key_id)

    #
    # Codecs work on a byte-level, so the underlying S3 object should
    # always be reading bytes.
    #
    if mode in (smart_open_s3.READ, smart_open_s3.READ_BINARY):
        s3_mode = smart_open_s3.READ_BINARY
    elif mode in (smart_open_s3.WRITE, smart_open_s3.WRITE_BINARY):
        s3_mode = smart_open_s3.WRITE_BINARY
    else:
        raise NotImplementedError('mode %r not implemented for S3' % mode)

    #
    # TODO: I'm not sure how to handle this with boto3.  Any ideas?
    #
    # https://github.com/boto/boto3/issues/334
    #
    # _setup_unsecured_mode()

    encoding = kwargs.get('encoding')
    errors = kwargs.get('errors', DEFAULT_ERRORS)
    fobj = smart_open_s3.open(parsed_uri.bucket_id, parsed_uri.key_id, s3_mode, **kwargs)
    decompressed_fobj = _CODECS[codec](fobj, mode)
    decoded_fobj = encoding_wrapper(decompressed_fobj, mode, encoding=encoding, errors=errors)
    return decoded_fobj