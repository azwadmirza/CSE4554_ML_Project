def _validate_name(name):
    '''
    Checks if the provided name fits Linode's labeling parameters.

    .. versionadded:: 2015.5.6

    name
        The VM name to validate
    '''
    name = str(name)
    name_length = len(name)
    regex = re.compile(r'^[a-zA-Z0-9][A-Za-z0-9_-]*[a-zA-Z0-9]$')

    if name_length < 3 or name_length > 48:
        ret = False
    elif not re.match(regex, name):
        ret = False
    else:
        ret = True

    if ret is False:
        log.warning(
            'A Linode label may only contain ASCII letters or numbers, dashes, and '
            'underscores, must begin and end with letters or numbers, and be at least '
            'three characters in length.'
        )

    return ret