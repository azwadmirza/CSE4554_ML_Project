def _mbcs_to_unicode_wrap(obj, vtype):
    '''
    Wraps _mbcs_to_unicode for use with registry vdata
    '''
    if vtype == 'REG_BINARY':
        # We should be able to leave it alone if the user has passed binary data in yaml with
        # binary !!
        # In python < 3 this should have type str and in python 3+ this should be a byte array
        return obj
    if isinstance(obj, list):
        return [_mbcs_to_unicode(x) for x in obj]
    elif isinstance(obj, six.integer_types):
        return obj
    else:
        return _mbcs_to_unicode(obj)