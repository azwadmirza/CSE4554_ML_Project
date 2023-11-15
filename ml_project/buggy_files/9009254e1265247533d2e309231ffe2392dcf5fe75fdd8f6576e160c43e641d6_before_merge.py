def encode_dict(data, encoding=None, errors='strict', preserve_dict_class=False, preserve_tuples=False):
    '''
    Encode all string values to bytes
    '''
    rv = data.__class__() if preserve_dict_class else {}
    for key, value in six.iteritems(data):
        if isinstance(key, tuple):
            key = encode_tuple(key, encoding, errors, preserve_dict_class) \
                if preserve_tuples \
                else encode_list(key, encoding, errors, preserve_dict_class, preserve_tuples)
        else:
            try:
                key = salt.utils.stringutils.to_bytes(key, encoding, errors)
            except TypeError:
                pass

        if isinstance(value, list):
            value = encode_list(value, encoding, errors, preserve_dict_class, preserve_tuples)
        elif isinstance(value, tuple):
            value = encode_tuple(value, encoding, errors, preserve_dict_class) \
                if preserve_tuples \
                else encode_list(value, encoding, errors, preserve_dict_class, preserve_tuples)
        elif isinstance(value, collections.Mapping):
            value = encode_dict(value, encoding, errors, preserve_dict_class, preserve_tuples)
        else:
            try:
                value = salt.utils.stringutils.to_bytes(value, encoding, errors)
            except TypeError:
                pass

        rv[key] = value
    return rv