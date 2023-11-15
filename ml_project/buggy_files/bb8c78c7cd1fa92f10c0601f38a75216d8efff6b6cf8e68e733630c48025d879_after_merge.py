def chgroups(name, groups, append=False, root=None):
    '''
    Change the groups to which this user belongs

    name
        User to modify

    groups
        Groups to set for the user

    append : False
        If ``True``, append the specified group(s). Otherwise, this function
        will replace the user's groups with the specified group(s).

    CLI Examples:

    .. code-block:: bash

        salt '*' user.chgroups foo wheel,root
        salt '*' user.chgroups foo wheel,root append=True
    '''
    if isinstance(groups, six.string_types):
        groups = groups.split(',')
    ugrps = set(list_groups(name))
    if ugrps == set(groups):
        return True
    cmd = ['usermod']

    if __grains__['kernel'] != 'OpenBSD':
        if append and __grains__['kernel'] != 'AIX':
            cmd.append('-a')
        cmd.append('-G')
    else:
        if append:
            cmd.append('-G')
        else:
            cmd.append('-S')

    if append and __grains__['kernel'] == 'AIX':
        cmd.extend([','.join(ugrps) + ',' + ','.join(groups), name])
    else:
        cmd.extend([','.join(groups), name])

    if root is not None and __grains__['kernel'] != 'AIX':
        cmd.extend(('-R', root))

    result = __salt__['cmd.run_all'](cmd, python_shell=False)
    # try to fallback on gpasswd to add user to localgroups
    # for old lib-pamldap support
    if __grains__['kernel'] != 'OpenBSD' and __grains__['kernel'] != 'AIX':
        if result['retcode'] != 0 and 'not found in' in result['stderr']:
            ret = True
            for group in groups:
                cmd = ['gpasswd', '-a', '{0}'.format(name), '{1}'.format(group)]
                if __salt__['cmd.retcode'](cmd, python_shell=False) != 0:
                    ret = False
            return ret
    return result['retcode'] == 0