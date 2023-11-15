def encode(data, encoding=None, errors='strict', preserve_dict_class=False, preserve_tuples=False):
    '''
    Generic function which will encode whichever type is passed, if necessary
    '''
    if isinstance(data, collections.Mapping):
        return encode_dict(data, encoding, errors, preserve_dict_class, preserve_tuples)
    elif isinstance(data, list):
        return encode_list(data, encoding, errors, preserve_dict_class, preserve_tuples)
    elif isinstance(data, tuple):
        return encode_tuple(data, encoding, errors, preserve_dict_class) \
            if preserve_tuples \
            else encode_list(data, encoding, errors, preserve_dict_class, preserve_tuples)
    else:
        try:
            return salt.utils.stringutils.to_bytes(data, encoding, errors)
        except TypeError:
            return data