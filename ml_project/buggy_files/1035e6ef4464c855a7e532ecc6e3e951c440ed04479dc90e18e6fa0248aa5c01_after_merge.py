def check_perms(name, ret, user, group, mode, attrs=None, follow_symlinks=False):
    '''
    Check the permissions on files, modify attributes and chown if needed. File
    attributes are only verified if lsattr(1) is installed.

    CLI Example:

    .. code-block:: bash

        salt '*' file.check_perms /etc/sudoers '{}' root root 400 ai

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
    perms['luser'] = cur['user']
    perms['lgroup'] = cur['group']
    perms['lmode'] = salt.utils.files.normalize_mode(cur['mode'])

    is_dir = os.path.isdir(name)
    is_link = os.path.islink(name)
    if not salt.utils.platform.is_windows() and not is_dir and not is_link:
        try:
            lattrs = lsattr(name)
        except SaltInvocationError:
            lattrs = None
        if lattrs is not None:
            # List attributes on file
            perms['lattrs'] = ''.join(lattrs.get(name, ''))
            # Remove attributes on file so changes can be enforced.
            if perms['lattrs']:
                chattr(name, operator='remove', attributes=perms['lattrs'])

    # user/group changes if needed, then check if it worked
    if user:
        if isinstance(user, int):
            user = uid_to_user(user)
        if (salt.utils.platform.is_windows() and
                user_to_uid(user) != user_to_uid(perms['luser'])
            ) or (
            not salt.utils.platform.is_windows() and user != perms['luser']
        ):
            perms['cuser'] = user

    if group:
        if isinstance(group, int):
            group = gid_to_group(group)
        if (salt.utils.platform.is_windows() and
                group_to_gid(group) != group_to_gid(perms['lgroup'])
            ) or (
                not salt.utils.platform.is_windows() and group != perms['lgroup']
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
        if (salt.utils.platform.is_windows() and
                user_to_uid(user) != user_to_uid(
                    get_user(name, follow_symlinks=follow_symlinks)) and
                user != ''
            ) or (
            not salt.utils.platform.is_windows() and
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
        if (salt.utils.platform.is_windows() and
                group_to_gid(group) != group_to_gid(
                    get_group(name, follow_symlinks=follow_symlinks)) and
                user != '') or (
            not salt.utils.platform.is_windows() and
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

    if not salt.utils.platform.is_windows() and not is_dir:
        # Replace attributes on file if it had been removed
        if perms.get('lattrs', ''):
            chattr(name, operator='add', attributes=perms['lattrs'])

    # Mode changes if needed
    if mode is not None:
        # File is a symlink, ignore the mode setting
        # if follow_symlinks is False
        if os.path.islink(name) and not follow_symlinks:
            pass
        else:
            mode = salt.utils.files.normalize_mode(mode)
            if mode != perms['lmode']:
                if __opts__['test'] is True:
                    ret['changes']['mode'] = mode
                else:
                    set_mode(name, mode)
                    if mode != salt.utils.files.normalize_mode(get_mode(name)):
                        ret['result'] = False
                        ret['comment'].append(
                            'Failed to change mode to {0}'.format(mode)
                        )
                    else:
                        ret['changes']['mode'] = mode

    # Modify attributes of file if needed
    if attrs is not None and not is_dir:
        # File is a symlink, ignore the mode setting
        # if follow_symlinks is False
        if os.path.islink(name) and not follow_symlinks:
            pass
        else:
            diff_attrs = _cmp_attrs(name, attrs)
            if diff_attrs is not None:
                if diff_attrs[0] is not None or diff_attrs[1] is not None:
                    if __opts__['test'] is True:
                        ret['changes']['attrs'] = attrs
                    else:
                        if diff_attrs[0] is not None:
                            chattr(name, operator="add", attributes=diff_attrs[0])
                        if diff_attrs[1] is not None:
                            chattr(name, operator="remove", attributes=diff_attrs[1])
                        cmp_attrs = _cmp_attrs(name, attrs)
                        if cmp_attrs[0] is not None or cmp_attrs[1] is not None:
                            ret['result'] = False
                            ret['comment'].append(
                                'Failed to change attributes to {0}'.format(attrs)
                            )
                        else:
                            ret['changes']['attrs'] = attrs

    # Only combine the comment list into a string
    # after all comments are added above
    if isinstance(orig_comment, six.string_types):
        if orig_comment:
            ret['comment'].insert(0, orig_comment)
        ret['comment'] = '; '.join(ret['comment'])

    # Set result to None at the very end of the function,
    # after all changes have been recorded above
    if __opts__['test'] is True and ret['changes']:
        ret['result'] = None

    return ret, perms