def check_perms(name, ret, user, group, mode, follow_symlinks=False):
    '''
    Check the permissions on files and chown if needed

    CLI Example:

    .. code-block:: bash

        salt '*' file.check_perms /etc/sudoers '{}' root root 400

    .. versionchanged:: 2014.1.3
        ``follow_symlinks`` option added
    '''
    name = os.path.expanduser(name)

    if not ret:
        ret = {'name': name,
               'changes': {},
               'comment': [],
               'result': True}
        orig_comment = ''
    else:
        orig_comment = ret['comment']
        ret['comment'] = []

    # Check permissions
    perms = {}
    cur = stats(name, follow_symlinks=follow_symlinks)
    if not cur:
        raise CommandExecutionError('{0} does not exist'.format(name))
    perms['luser'] = cur['user']
    perms['lgroup'] = cur['group']
    perms['lmode'] = __salt__['config.manage_mode'](cur['mode'])

    # Mode changes if needed
    if mode is not None:
        # File is a symlink, ignore the mode setting
        # if follow_symlinks is False
        if os.path.islink(name) and not follow_symlinks:
            pass
        else:
            mode = __salt__['config.manage_mode'](mode)
            if mode != perms['lmode']:
                if __opts__['test'] is True:
                    ret['changes']['mode'] = mode
                else:
                    set_mode(name, mode)
                    if mode != __salt__['config.manage_mode'](get_mode(name)):
                        ret['result'] = False
                        ret['comment'].append(
                            'Failed to change mode to {0}'.format(mode)
                        )
                    else:
                        ret['changes']['mode'] = mode
    # user/group changes if needed, then check if it worked
    if user:
        if isinstance(user, int):
            user = uid_to_user(user)
        if (salt.utils.is_windows() and
                user_to_uid(user) != user_to_uid(perms['luser'])
            ) or (
            not salt.utils.is_windows() and user != perms['luser']
        ):
            perms['cuser'] = user

    if group:
        if isinstance(group, int):
            group = gid_to_group(group)
        if (salt.utils.is_windows() and
                group_to_gid(group) != group_to_gid(perms['lgroup'])
            ) or (
                not salt.utils.is_windows() and group != perms['lgroup']
        ):
            perms['cgroup'] = group

    if 'cuser' in perms or 'cgroup' in perms:
        if not __opts__['test']:
            if os.path.islink(name) and not follow_symlinks:
                chown_func = lchown
            else:
                chown_func = chown
            if user is None:
                user = perms['luser']
            if group is None:
                group = perms['lgroup']
            try:
                chown_func(name, user, group)
            except OSError:
                ret['result'] = False

    if user:
        if isinstance(user, int):
            user = uid_to_user(user)
        if (salt.utils.is_windows() and
                user_to_uid(user) != user_to_uid(
                    get_user(name, follow_symlinks=follow_symlinks)) and
                user != ''
            ) or (
            not salt.utils.is_windows() and
                user != get_user(name, follow_symlinks=follow_symlinks) and
                user != ''
        ):
            if __opts__['test'] is True:
                ret['changes']['user'] = user
            else:
                ret['result'] = False
                ret['comment'].append('Failed to change user to {0}'
                                          .format(user))
        elif 'cuser' in perms and user != '':
            ret['changes']['user'] = user
    if group:
        if isinstance(group, int):
            group = gid_to_group(group)
        if (salt.utils.is_windows() and
                group_to_gid(group) != group_to_gid(
                    get_group(name, follow_symlinks=follow_symlinks)) and
                user != '') or (
            not salt.utils.is_windows() and
                group != get_group(name, follow_symlinks=follow_symlinks) and
                user != ''
        ):
            if __opts__['test'] is True:
                ret['changes']['group'] = group
            else:
                ret['result'] = False
                ret['comment'].append('Failed to change group to {0}'
                                      .format(group))
        elif 'cgroup' in perms and user != '':
            ret['changes']['group'] = group

    if isinstance(orig_comment, six.string_types):
        if orig_comment:
            ret['comment'].insert(0, orig_comment)
        ret['comment'] = '; '.join(ret['comment'])
    if __opts__['test'] is True and ret['changes']:
        ret['result'] = None
    return ret, perms