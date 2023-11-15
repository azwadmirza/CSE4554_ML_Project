def _to_unicode(vdata):
    '''
    Converts from current users character encoding to unicode. Use this for
    parameters being pass to reg functions
    '''
    # None does not convert to Unicode
    if vdata is None:
        return None
    return salt.utils.stringutils.to_unicode(vdata, 'utf-8')