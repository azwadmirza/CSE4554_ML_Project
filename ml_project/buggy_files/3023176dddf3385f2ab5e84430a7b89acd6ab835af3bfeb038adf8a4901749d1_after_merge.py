def encode_list(data, encoding=None, errors='strict', keep=False,
                preserve_dict_class=False, preserve_tuples=False):
    '''
    Encode all string values to bytes
    '''
    rv = []
    for item in data:
        if isinstance(item, list):
            item = encode_list(item, encoding, errors, keep,
                               preserve_dict_class, preserve_tuples)
        elif isinstance(item, tuple):
            item = encode_tuple(item, encoding, errors, keep, preserve_dict_class) \
                if preserve_tuples \
                else encode_list(item, encoding, errors, keep,
                                 preserve_dict_class, preserve_tuples)
        elif isinstance(item, collections.Mapping):
            item = encode_dict(item, encoding, errors, keep,
                               preserve_dict_class, preserve_tuples)
        else:
            try:
                item = salt.utils.stringutils.to_bytes(item, encoding, errors)
            except TypeError:
                pass
            except UnicodeEncodeError:
                if not keep:
                    raise

        rv.append(item)
    return rv