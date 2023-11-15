def get_password_hasher(scheme):
    """Retrieve the hasher corresponding to :keyword:`scheme`.

    If no class is found, `PLAINHasher` is returned.

    :param str scheme: a valid scheme name
    :rtype: PasswordHasher sub class
    :return: The hasher class
    """
    try:
        scheme = scheme.replace('-', '')
        hasher = globals()['%sHasher' % scheme.upper()]
    except KeyError:
        hasher = PLAINHasher
    return hasher