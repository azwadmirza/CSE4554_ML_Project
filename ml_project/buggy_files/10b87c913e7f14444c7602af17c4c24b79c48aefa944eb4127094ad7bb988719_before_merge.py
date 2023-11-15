def decode_tuple(data, encoding=None, errors='strict', keep=False,
                 normalize=False, preserve_dict_class=False):
    '''
    Decode all string values to Unicode
    '''
    return tuple(
        decode_list(data, encoding, errors, keep, normalize,
                    preserve_dict_class, True)
    )