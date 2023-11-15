def _to_unicode(vdata):
    '''
    Converts from current users character encoding to unicode. Use this for
    parameters being pass to reg functions
    '''
    return salt.utils.stringutils.to_unicode(vdata, 'utf-8')