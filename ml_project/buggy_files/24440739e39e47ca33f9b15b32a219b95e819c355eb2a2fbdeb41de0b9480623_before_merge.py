def decode_list(data, encoding=None, errors='strict', keep=False,
                normalize=False, preserve_dict_class=False,
                preserve_tuples=False):
    '''
    Decode all string values to Unicode
    '''
    rv = []
    for item in data:
        if isinstance(item, list):
            item = decode_list(item, encoding, errors, keep, normalize,
                               preserve_dict_class, preserve_tuples)
        elif isinstance(item, tuple):
            item = decode_tuple(item, encoding, errors, keep, normalize,
                                preserve_dict_class) \
                if preserve_tuples \
                else decode_list(item, encoding, errors, keep, normalize,
                                 preserve_dict_class, preserve_tuples)
        elif isinstance(item, collections.Mapping):
            item = decode_dict(item, encoding, errors, keep, normalize,
                               preserve_dict_class, preserve_tuples)
        else:
            try:
                item = salt.utils.stringutils.to_unicode(
                    item, encoding, errors, normalize)
            except TypeError:
                # to_unicode raises a TypeError when input is not a
                # string/bytestring/bytearray. This is expected and simply
                # means we are going to leave the value as-is.
                pass
            except UnicodeDecodeError:
                if not keep:
                    raise

        rv.append(item)
    return rv