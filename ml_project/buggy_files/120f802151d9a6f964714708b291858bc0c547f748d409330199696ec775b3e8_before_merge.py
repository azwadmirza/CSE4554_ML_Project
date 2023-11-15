def decode(data, encoding=None, errors='strict', keep=False,
           normalize=False, preserve_dict_class=False, preserve_tuples=False):
    '''
    Generic function which will decode whichever type is passed, if necessary

    If `strict` is True, and `keep` is False, and we fail to decode, a
    UnicodeDecodeError will be raised. Passing `keep` as True allows for the
    original value to silently be returned in cases where decoding fails. This
    can be useful for cases where the data passed to this function is likely to
    contain binary blobs, such as in the case of cp.recv.

    If `normalize` is True, then unicodedata.normalize() will be used to
    normalize unicode strings down to a single code point per glyph. It is
    recommended not to normalize unless you know what you're doing. For
    instance, if `data` contains a dictionary, it is possible that normalizing
    will lead to data loss because the following two strings will normalize to
    the same value:

    - u'\\u044f\\u0438\\u0306\\u0446\\u0430.txt'
    - u'\\u044f\\u0439\\u0446\\u0430.txt'

    One good use case for normalization is in the test suite. For example, on
    some platforms such as Mac OS, os.listdir() will produce the first of the
    two strings above, in which "й" is represented as two code points (i.e. one
    for the base character, and one for the breve mark). Normalizing allows for
    a more reliable test case.
    '''
    if isinstance(data, collections.Mapping):
        return decode_dict(data, encoding, errors, keep, normalize,
                           preserve_dict_class, preserve_tuples)
    elif isinstance(data, list):
        return decode_list(data, encoding, errors, keep, normalize,
                           preserve_dict_class, preserve_tuples)
    elif isinstance(data, tuple):
        return decode_tuple(data, encoding, errors, keep, normalize,
                            preserve_dict_class) \
            if preserve_tuples \
            else decode_list(data, encoding, errors, keep, normalize,
                             preserve_dict_class, preserve_tuples)
    else:
        try:
            data = salt.utils.stringutils.to_unicode(
                data, encoding, errors, normalize)
        except TypeError:
            # to_unicode raises a TypeError when input is not a
            # string/bytestring/bytearray. This is expected and simply means we
            # are going to leave the value as-is.
            pass
        except UnicodeDecodeError:
            if not keep:
                raise
        return data