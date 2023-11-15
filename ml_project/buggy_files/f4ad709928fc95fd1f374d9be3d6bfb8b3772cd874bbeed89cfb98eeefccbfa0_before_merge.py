def active():
    '''
    Return current active profile

    CLI Example:

    .. code-block:: bash

        salt '*' tuned.active
    '''

    # turn off all profiles
    result = __salt__['cmd.run']('tuned-adm active')
    pattern = re.compile(r'''(?P<stmt>Current active profile:) (?P<profile>\w+.*)''')
    match = re.match(pattern, result)
    return '{0}'.format(match.group('profile'))