def decode_tuple(data, encoding=None, errors='strict', preserve_dict_class=False):
    '''
    Decode all string values to Unicode
    '''
    return tuple(decode_list(data, encoding, errors, preserve_dict_class, True))