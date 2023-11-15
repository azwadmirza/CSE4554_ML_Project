def get_offset():
    '''
    Get current numeric timezone offset from UCT (i.e. -0700)

    CLI Example:

    .. code-block:: bash

        salt '*' timezone.get_offset
    '''
    string = False
    zone = __salt__['cmd.run'](['tzutil', '/g'], python_shell=False)
    prev = ''
    zone_list = __salt__['cmd.run'](['tzutil', '/l'],
                                    python_shell=False,
                                    output_loglevel='trace').splitlines()
    for line in zone_list:
        if zone == line:
            string = prev
            break
        else:
            prev = line

    if not string:
        return False

    reg = re.search(r"\(UTC(.\d\d:\d\d)\) .*", string, re.M)
    if not reg:
        ret = '0000'
    else:
        ret = reg.group(1).replace(':', '')

    return ret