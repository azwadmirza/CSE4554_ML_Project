def decode(data, encoding=None, errors='strict', preserve_dict_class=False, preserve_tuples=False):
    '''
    Generic function which will decode whichever type is passed, if necessary
    '''
    if isinstance(data, collections.Mapping):
        return decode_dict(data, encoding, errors, preserve_dict_class, preserve_tuples)
    elif isinstance(data, list):
        return decode_list(data, encoding, errors, preserve_dict_class, preserve_tuples)
    elif isinstance(data, tuple):
        return decode_tuple(data, encoding, errors, preserve_dict_class) \
            if preserve_tuples \
            else decode_list(data, encoding, errors, preserve_dict_class, preserve_tuples)
    else:
        try:
            return salt.utils.stringutils.to_unicode(data, encoding, errors)
        except TypeError:
            return data