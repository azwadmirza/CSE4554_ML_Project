def to_unicode(s, encoding=None):
    '''
    Given str or unicode, return unicode (str for python 3)
    '''
    if s is None:
        return s
    if six.PY3:
        return to_str(s, encoding)
    else:
        if isinstance(s, str):
            return s.decode(encoding or __salt_system_encoding__)
        return unicode(s)  # pylint: disable=incompatible-py3-code