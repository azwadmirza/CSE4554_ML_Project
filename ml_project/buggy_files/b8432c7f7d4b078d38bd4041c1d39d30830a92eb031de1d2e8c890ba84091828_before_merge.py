def open(bucket_id, key_id, mode, **kwargs):
    logger.debug('%r', locals())
    if mode not in MODES:
        raise NotImplementedError('bad mode: %r expected one of %r' % (mode, MODES))

    buffer_size = kwargs.pop("buffer_size", io.DEFAULT_BUFFER_SIZE)
    encoding = kwargs.pop("encoding", "utf-8")
    errors = kwargs.pop("errors", None)
    newline = kwargs.pop("newline", None)
    line_buffering = kwargs.pop("line_buffering", False)
    s3_min_part_size = kwargs.pop("s3_min_part_size", DEFAULT_MIN_PART_SIZE)

    if mode in (READ, READ_BINARY):
        fileobj = BufferedInputBase(bucket_id, key_id, **kwargs)
    elif mode in (WRITE, WRITE_BINARY):
        fileobj = BufferedOutputBase(bucket_id, key_id, min_part_size=s3_min_part_size, **kwargs)
    else:
        assert False

    if mode in (READ, WRITE):
        return io.TextIOWrapper(fileobj, encoding=encoding, errors=errors,
                                newline=newline, line_buffering=line_buffering)
    elif mode in (READ_BINARY, WRITE_BINARY):
        return fileobj
    else:
        assert False