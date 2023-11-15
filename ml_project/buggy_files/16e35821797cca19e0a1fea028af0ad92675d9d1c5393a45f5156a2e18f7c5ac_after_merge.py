def add(name,
        password=None,
        fullname=None,
        description=None,
        groups=None,
        home=None,
        homedrive=None,
        profile=None,
        logonscript=None):
    '''
    Add a user to the minion.

    Args:
        name (str): User name

        password (str, optional): User's password in plain text.

        fullname (str, optional): The user's full name.

        description (str, optional): A brief description of the user account.

        groups (str, optional): A list of groups to add the user to.
            (see chgroups)

        home (str, optional): The path to the user's home directory.

        homedrive (str, optional): The drive letter to assign to the home
            directory. Must be the Drive Letter followed by a colon. ie: U:

        profile (str, optional): An explicit path to a profile. Can be a UNC or
            a folder on the system. If left blank, windows uses it's default
            profile directory.

        logonscript (str, optional): Path to a login script to run when the user
            logs on.

    Returns:
        bool: True if successful. False is unsuccessful.

    CLI Example:

    .. code-block:: bash

        salt '*' user.add name password
    '''
    if six.PY2:
        name = _to_unicode(name)
        password = _to_unicode(password)
        fullname = _to_unicode(fullname)
        description = _to_unicode(description)
        home = _to_unicode(home)
        homedrive = _to_unicode(homedrive)
        profile = _to_unicode(profile)
        logonscript = _to_unicode(logonscript)

    user_info = {}
    if name:
        user_info['name'] = name
    else:
        return False
    user_info['password'] = password
    user_info['priv'] = win32netcon.USER_PRIV_USER
    user_info['home_dir'] = home
    user_info['comment'] = description
    user_info['flags'] = win32netcon.UF_SCRIPT
    user_info['script_path'] = logonscript

    try:
        win32net.NetUserAdd(None, 1, user_info)
    except win32net.error as exc:
        (number, context, message) = exc
        log.error('Failed to create user {0}'.format(name))
        log.error('nbr: {0}'.format(exc.winerror))
        log.error('ctx: {0}'.format(exc.funcname))
        log.error('msg: {0}'.format(exc.strerror))
        return False

    update(name=name,
           homedrive=homedrive,
           profile=profile,
           fullname=fullname)

    ret = chgroups(name, groups) if groups else True

    return ret