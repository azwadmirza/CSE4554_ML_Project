def decode(data, encoding=None, errors='strict', keep=False,
           preserve_dict_class=False, preserve_tuples=False):
    '''
    Generic function which will decode whichever type is passed, if necessary

    If `strict` is True, and `keep` is False, and we fail to decode, a
    UnicodeDecodeError will be raised. Passing `keep` as True allows for the
    original value to silently be returned in cases where decoding fails. This
    can be useful for cases where the data passed to this function is likely to
    contain binary blobs, such as in the case of cp.recv.
    '''
    if isinstance(data, collections.Mapping):
        return decode_dict(data, encoding, errors, keep,
                           preserve_dict_class, preserve_tuples)
    elif isinstance(data, list):
        return decode_list(data, encoding, errors, keep,
                           preserve_dict_class, preserve_tuples)
    elif isinstance(data, tuple):
        return decode_tuple(data, encoding, errors, keep, preserve_dict_class) \
            if preserve_tuples \
            else decode_list(data, encoding, errors, keep,
                             preserve_dict_class, preserve_tuples)
    else:
        try:
            return salt.utils.stringutils.to_unicode(data, encoding, errors)
        except TypeError:
            pass
        except UnicodeDecodeError:
            if not keep:
                raise
        return data