def decode_dict(data, encoding=None, errors='strict', keep=False,
                normalize=False, preserve_dict_class=False,
                preserve_tuples=False):
    '''
    Decode all string values to Unicode
    '''
    # Make sure we preserve OrderedDicts
    rv = data.__class__() if preserve_dict_class else {}
    for key, value in six.iteritems(data):
        if isinstance(key, tuple):
            key = decode_tuple(key, encoding, errors, keep, normalize,
                               preserve_dict_class) \
                if preserve_tuples \
                else decode_list(key, encoding, errors, keep, normalize,
                                 preserve_dict_class, preserve_tuples)
        else:
            try:
                key = salt.utils.stringutils.to_unicode(
                    key, encoding, errors, normalize)
            except TypeError:
                # to_unicode raises a TypeError when input is not a
                # string/bytestring/bytearray. This is expected and simply
                # means we are going to leave the value as-is.
                pass
            except UnicodeDecodeError:
                if not keep:
                    raise

        if isinstance(value, list):
            value = decode_list(value, encoding, errors, keep, normalize,
                                preserve_dict_class, preserve_tuples)
        elif isinstance(value, tuple):
            value = decode_tuple(value, encoding, errors, keep, normalize,
                                 preserve_dict_class) \
                if preserve_tuples \
                else decode_list(value, encoding, errors, keep, normalize,
                                 preserve_dict_class, preserve_tuples)
        elif isinstance(value, collections.Mapping):
            value = decode_dict(value, encoding, errors, keep, normalize,
                                preserve_dict_class, preserve_tuples)
        else:
            try:
                value = salt.utils.stringutils.to_unicode(
                    value, encoding, errors, normalize)
            except TypeError:
                # to_unicode raises a TypeError when input is not a
                # string/bytestring/bytearray. This is expected and simply
                # means we are going to leave the value as-is.
                pass
            except UnicodeDecodeError:
                if not keep:
                    raise

        rv[key] = value
    return rv