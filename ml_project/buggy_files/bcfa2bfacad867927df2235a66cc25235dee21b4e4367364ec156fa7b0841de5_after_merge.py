def dump(obj, fp, ensure_ascii=True):
    """
    Attempt to json.dump() an object to a 'file'. This function provides additional info if the object can't
    be serialized.

    :param obj: the object to serialize.
    :param fp: the file-like object to write to.
    :param ensure_ascii: allow binary strings to be sent
    """
    try:
        json.dump(obj, fp, ensure_ascii=ensure_ascii)
    except UnicodeDecodeError as e:
        undumpables = _scan_iterable(obj)
        traces = '\n\t'.join(['->'.join(u) for u in undumpables])
        error = UnicodeDecodeError(e.encoding, str(obj), e.start, e.end, "could not dump:\n\t%s" % traces)
        error.message = str(error)
        raise error