def info(name):
    '''
    Return information for the specified user

    CLI Example:

    .. code-block:: bash

        salt '*' shadow.info root
    '''
    if HAS_SPWD:
        try:
            data = spwd.getspnam(name)
            ret = {
                'name': data.sp_nam,
                'passwd': data.sp_pwd,
                'lstchg': data.sp_lstchg,
                'min': data.sp_min,
                'max': data.sp_max,
                'warn': data.sp_warn,
                'inact': data.sp_inact,
                'expire': data.sp_expire}
        except KeyError:
            ret = {
                'name': '',
                'passwd': '',
                'lstchg': '',
                'min': '',
                'max': '',
                'warn': '',
                'inact': '',
                'expire': ''}
        return ret

    # SmartOS joyent_20130322T181205Z does not have spwd, but not all is lost
    # Return what we can know
    ret = {
        'name': '',
        'passwd': '',
        'lstchg': '',
        'min': '',
        'max': '',
        'warn': '',
        'inact': '',
        'expire': ''}

    try:
        data = pwd.getpwnam(name)
        ret.update({
            'name': name
        })
    except KeyError:
        return ret

    # To compensate for lack of spwd module, read in password hash from /etc/shadow
    s_file = '/etc/shadow'
    if not os.path.isfile(s_file):
        return ret
    with salt.utils.fopen(s_file, 'rb') as ifile:
        for line in ifile:
            comps = line.strip().split(':')
            if comps[0] == name:
                ret.update({'passwd': comps[1]})

    # For SmartOS `passwd -s <username>` and the output format is:
    #   name status mm/dd/yy min max warn
    #
    # Fields:
    #  1. Name: username
    #  2. Status:
    #      - LK: locked
    #      - NL: no login
    #      - NP: No password
    #      - PS: Password
    #  3. Last password change
    #  4. Minimum age
    #  5. Maximum age
    #  6. Warning period

    output = __salt__['cmd.run_all']('passwd -s {0}'.format(name))
    if output['retcode'] != 0:
        return ret

    fields = output['stdout'].split()
    if len(fields) == 2:
        # For example:
        #   root      NL
        return ret
    # We have all fields:
    #   buildbot L 05/09/2013 0 99999 7
    ret.update({
        'name': data.pw_name,
        'lstchg': fields[2],
        'min': int(fields[3]),
        'max': int(fields[4]),
        'warn': int(fields[5]),
        'inact': '',
        'expire': ''
    })
    return ret