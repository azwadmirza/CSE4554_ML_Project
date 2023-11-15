def _cmp_attrs(path, attrs):
    '''
    .. versionadded:: 2018.3.0

    Compare attributes of a given file to given attributes.
    Returns a pair (list) where first item are attributes to
    add and second item are to be removed.

    Please take into account when using this function that some minions will
    not have lsattr installed.

    path
        path to file to compare attributes with.

    attrs
        string of attributes to compare against a given file
    '''
    diff = [None, None]

    # lsattr for AIX is not the same thing as lsattr for linux.
    if salt.utils.platform.is_aix():
        return None

    try:
        lattrs = lsattr(path).get(path, '')
    except AttributeError:
        # lsattr not installed
        return None

    old = [chr for chr in lattrs if chr not in attrs]
    if len(old) > 0:
        diff[1] = ''.join(old)

    new = [chr for chr in attrs if chr not in lattrs]
    if len(new) > 0:
        diff[0] = ''.join(new)

    return diff