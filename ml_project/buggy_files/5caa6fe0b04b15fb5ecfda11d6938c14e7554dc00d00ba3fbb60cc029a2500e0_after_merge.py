def encode_tuple(data, encoding=None, errors='strict', keep=False,
                 preserve_dict_class=False):
    '''
    Encode all string values to Unicode
    '''
    return tuple(
        encode_list(data, encoding, errors, keep, preserve_dict_class, True))