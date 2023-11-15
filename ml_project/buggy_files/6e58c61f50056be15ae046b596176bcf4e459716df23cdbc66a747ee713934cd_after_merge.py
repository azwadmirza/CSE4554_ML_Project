def refresh_db():
    '''
    Force a repository refresh by calling ``zypper refresh --force``, return a dict::

        {'<database name>': Bool}

    CLI Example:

    .. code-block:: bash

        salt '*' pkg.refresh_db
    '''
    ret = {}
    out = __zypper__.refreshable.call('refresh', '--force')

    for line in out.splitlines():
        if not line:
            continue
        if line.strip().startswith('Repository') and '\'' in line:
            try:
                key = line.split('\'')[1].strip()
                if 'is up to date' in line:
                    ret[key] = False
            except IndexError:
                continue
        elif line.strip().startswith('Building') and '\'' in line:
            key = line.split('\'')[1].strip()
            if 'done' in line:
                ret[key] = True
    return ret