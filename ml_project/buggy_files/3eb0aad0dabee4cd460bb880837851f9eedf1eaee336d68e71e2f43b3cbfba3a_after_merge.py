def encode(data, encoding=None, errors='strict', keep=False,
           preserve_dict_class=False, preserve_tuples=False):
    '''
    Generic function which will encode whichever type is passed, if necessary

    If `strict` is True, and `keep` is False, and we fail to encode, a
    UnicodeEncodeError will be raised. Passing `keep` as True allows for the
    original value to silently be returned in cases where encoding fails. This
    can be useful for cases where the data passed to this function is likely to
    contain binary blobs.
    '''
    if isinstance(data, collections.Mapping):
        return encode_dict(data, encoding, errors, keep,
                           preserve_dict_class, preserve_tuples)
    elif isinstance(data, list):
        return encode_list(data, encoding, errors, keep,
                           preserve_dict_class, preserve_tuples)
    elif isinstance(data, tuple):
        return encode_tuple(data, encoding, errors, keep, preserve_dict_class) \
            if preserve_tuples \
            else encode_list(data, encoding, errors, keep,
                             preserve_dict_class, preserve_tuples)
    else:
        try:
            return salt.utils.stringutils.to_bytes(data, encoding, errors)
        except TypeError:
            pass
        except UnicodeEncodeError:
            if not keep:
                raise
        return data