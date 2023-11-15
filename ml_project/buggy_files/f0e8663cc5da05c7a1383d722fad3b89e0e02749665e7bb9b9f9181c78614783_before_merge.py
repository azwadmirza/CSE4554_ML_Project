def decode_dict(data, encoding=None, errors='strict', preserve_dict_class=False, preserve_tuples=False):
    '''
    Decode all string values to Unicode
    '''
    # Make sure we preserve OrderedDicts
    rv = data.__class__() if preserve_dict_class else {}
    for key, value in six.iteritems(data):
        if isinstance(key, tuple):
            key = decode_tuple(key, encoding, errors, preserve_dict_class) \
                if preserve_tuples \
                else decode_list(key, encoding, errors, preserve_dict_class, preserve_tuples)
        else:
            try:
                key = salt.utils.stringutils.to_unicode(key, encoding, errors)
            except TypeError:
                pass

        if isinstance(value, list):
            value = decode_list(value, encoding, errors, preserve_dict_class, preserve_tuples)
        elif isinstance(value, tuple):
            value = decode_tuple(value, encoding, errors, preserve_dict_class) \
                if preserve_tuples \
                else decode_list(value, encoding, errors, preserve_dict_class, preserve_tuples)
        elif isinstance(value, collections.Mapping):
            value = decode_dict(value, encoding, errors, preserve_dict_class, preserve_tuples)
        else:
            try:
                value = salt.utils.stringutils.to_unicode(value, encoding, errors)
            except TypeError:
                pass

        rv[key] = value
    return rv