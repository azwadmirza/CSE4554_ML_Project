def active():
    '''
    Return current active profile

    CLI Example:

    .. code-block:: bash

        salt '*' tuned.active
    '''

    # turn off all profiles
    result = __salt__['cmd.run_all']('tuned-adm active', ignore_retcode=True)
    if result['retcode'] != 0:
        return "none"
    pattern = re.compile(r'''(?P<stmt>Current active profile:) (?P<profile>\w+.*)''')
    match = re.match(pattern, result['stdout'])
    return '{0}'.format(match.group('profile'))