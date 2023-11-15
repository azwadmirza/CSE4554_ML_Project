def add(name,
        uid=None,
        gid=None,
        groups=None,
        home=None,
        shell=None,
        unique=True,
        system=False,
        fullname='',
        roomnumber='',
        workphone='',
        homephone='',
        createhome=True,
        loginclass=None,
        root=None):
    '''
    Add a user to the minion

    CLI Example:

    .. code-block:: bash

        salt '*' user.add name <uid> <gid> <groups> <home> <shell>
    '''
    cmd = ['useradd']
    if shell:
        cmd.extend(['-s', shell])
    if uid not in (None, ''):
        cmd.extend(['-u', str(uid)])
    if gid not in (None, ''):
        cmd.extend(['-g', str(gid)])
    elif groups is not None and name in groups:
        defs_file = '/etc/login.defs'
        if __grains__['kernel'] != 'OpenBSD':
            try:
                with salt.utils.fopen(defs_file) as fp_:
                    for line in fp_:
                        if 'USERGROUPS_ENAB' not in line[:15]:
                            continue

                        if 'yes' in line:
                            cmd.extend([
                                '-g', str(__salt__['file.group_to_gid'](name))
                            ])

                        # We found what we wanted, let's break out of the loop
                        break
            except OSError:
                log.debug(
                    'Error reading ' + defs_file,
                    exc_info_on_loglevel=logging.DEBUG
                )
        else:
            usermgmt_file = '/etc/usermgmt.conf'
            try:
                with salt.utils.fopen(usermgmt_file) as fp_:
                    for line in fp_:
                        if 'group' not in line[:5]:
                            continue

                        cmd.extend([
                            '-g', str(line.split()[-1])
                        ])

                        # We found what we wanted, let's break out of the loop
                        break
            except OSError:
                # /etc/usermgmt.conf not present: defaults will be used
                pass

    if createhome:
        cmd.append('-m')
    elif (__grains__['kernel'] != 'NetBSD'
            and __grains__['kernel'] != 'OpenBSD'):
        cmd.append('-M')

    if home is not None:
        cmd.extend(['-d', home])

    if not unique:
        cmd.append('-o')

    if (system
        and __grains__['kernel'] != 'NetBSD'
        and __grains__['kernel'] != 'OpenBSD'):
        cmd.append('-r')

    if __grains__['kernel'] == 'OpenBSD':
        if loginclass is not None:
            cmd.extend(['-L', loginclass])

    cmd.append(name)

    if root is not None:
        cmd.extend(('-R', root))

    ret = __salt__['cmd.run_all'](cmd, python_shell=False)

    if ret['retcode'] != 0:
        return False

    # At this point, the user was successfully created, so return true
    # regardless of the outcome of the below functions. If there is a
    # problem wth changing any of the user's info below, it will be raised
    # in a future highstate call. If anyone has a better idea on how to do
    # this, feel free to change it, but I didn't think it was a good idea
    # to return False when the user was successfully created since A) the
    # user does exist, and B) running useradd again would result in a
    # nonzero exit status and be interpreted as a False result.
    if groups:
        chgroups(name, groups)
    if fullname:
        chfullname(name, fullname)
    if roomnumber:
        chroomnumber(name, roomnumber)
    if workphone:
        chworkphone(name, workphone)
    if homephone:
        chhomephone(name, homephone)
    return True