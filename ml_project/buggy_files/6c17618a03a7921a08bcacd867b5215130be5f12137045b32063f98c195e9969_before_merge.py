def directory(name,
              user=None,
              group=None,
              recurse=None,
              dir_mode=None,
              file_mode=None,
              makedirs=False,
              clean=False,
              require=None,
              exclude_pat=None,
              follow_symlinks=False,
              force=False,
              backupname=None,
              **kwargs):
    '''
    Ensure that a named directory is present and has the right perms

    name
        The location to create or manage a directory

    user
        The user to own the directory; this defaults to the user salt is
        running as on the minion

    group
        The group ownership set for the directory; this defaults to the group
        salt is running as on the minion. On Windows, this is ignored

    recurse
        Enforce user/group ownership and mode of directory recursively. Accepts
        a list of strings representing what you would like to recurse.  If
        'mode' is defined, will recurse on both 'file_mode' and 'dir_mode' if
        they are defined.
        Example:

        .. code-block:: yaml

            /var/log/httpd:
                file.directory:
                - user: root
                - group: root
                - dir_mode: 755
                - file_mode: 644
                - recurse:
                    - user
                    - group
                    - mode

    dir_mode / mode
        The permissions mode to set any directories created. Not supported on
        Windows

    file_mode
        The permissions mode to set any files created if 'mode' is run in
        'recurse'. This defaults to dir_mode. Not supported on Windows

    makedirs
        If the directory is located in a path without a parent directory, then
        the state will fail. If makedirs is set to True, then the parent
        directories will be created to facilitate the creation of the named
        file.

    clean
        Make sure that only files that are set up by salt and required by this
        function are kept. If this option is set then everything in this
        directory will be deleted unless it is required.

    require
        Require other resources such as packages or files

    exclude_pat
        When 'clean' is set to True, exclude this pattern from removal list
        and preserve in the destination.

    follow_symlinks : False
        If the desired path is a symlink (or ``recurse`` is defined and a
        symlink is encountered while recursing), follow it and check the
        permissions of the directory/file to which the symlink points.

        .. versionadded:: 2014.1.4

    force
        If the name of the directory exists and is not a directory and
        force is set to False, the state will fail. If force is set to
        True, the file in the way of the directory will be deleted to
        make room for the directory, unless backupname is set,
        then it will be renamed.

        .. versionadded:: 2014.7.0

    backupname
        If the name of the directory exists and is not a directory, it will be
        renamed to the backupname. If the backupname already
        exists and force is False, the state will fail. Otherwise, the
        backupname will be removed first.

        .. versionadded:: 2014.7.0

    '''
    # Remove trailing slash, if present
    if name[-1] == '/':
        name = name[:-1]

    user = _test_owner(kwargs, user=user)
    if salt.utils.is_windows():
        if group is not None:
            log.warning(
                'The group argument for {0} has been ignored as this is '
                'a Windows system.'.format(name)
            )
        group = user

    if 'mode' in kwargs and not dir_mode:
        dir_mode = kwargs.get('mode', [])

    if not file_mode:
        file_mode = dir_mode

    # Make sure that leading zeros stripped by YAML loader are added back
    dir_mode = __salt__['config.manage_mode'](dir_mode)
    file_mode = __salt__['config.manage_mode'](file_mode)

    ret = {'name': name,
           'changes': {},
           'result': True,
           'comment': ''}
    u_check = _check_user(user, group)
    if u_check:
        # The specified user or group do not exist
        return _error(ret, u_check)
    if not os.path.isabs(name):
        return _error(
            ret, 'Specified file {0} is not an absolute path'.format(name))
    if os.path.isfile(name):
        if backupname is not None:
            # Make a backup first
            if os.path.lexists(backupname):
                if not force:
                    return _error(ret, ((
                        'File exists where the backup target {0} should go'
                    ).format(backupname)))
                elif os.path.isfile(backupname):
                    os.remove(backupname)
                elif os.path.isdir(backupname):
                    shutil.rmtree(backupname)
                else:
                    return _error(ret, ((
                        'Something exists where the backup target {0}'
                        'should go'
                    ).format(backupname)))
            os.rename(name, backupname)
        elif force:
            # Remove whatever is in the way
            if os.path.isfile(name):
                os.remove(name)
                ret['changes']['forced'] = 'File was forcibly replaced'
            else:
                shutil.rmtree(name)
        else:
            return _error(
                ret, 'Specified location {0} exists and is a file'.format(name))
    if __opts__['test']:
        ret['result'], ret['comment'] = _check_directory(
            name,
            user,
            group,
            recurse or [],
            dir_mode,
            clean,
            require,
            exclude_pat)
        return ret

    if not os.path.isdir(name):
        # The dir does not exist, make it
        if not os.path.isdir(os.path.dirname(name)):
            # The parent directory does not exist, create them
            if makedirs:
                __salt__['file.makedirs'](
                    name, user=user, group=group, mode=dir_mode
                )
            else:
                return _error(
                    ret, 'No directory to create {0} in'.format(name))

        __salt__['file.mkdir'](
            name, user=user, group=group, mode=dir_mode
        )
        ret['changes'][name] = 'New Dir'

    if not os.path.isdir(name):
        return _error(ret, 'Failed to create directory {0}'.format(name))

    # Check permissions
    ret, perms = __salt__['file.check_perms'](name,
                                              ret,
                                              user,
                                              group,
                                              dir_mode,
                                              follow_symlinks)

    if recurse:
        if not isinstance(recurse, list):
            ret['result'] = False
            ret['comment'] = '"recurse" must be formed as a list of strings'
        elif not set(['user', 'group', 'mode']) >= set(recurse):
            ret['result'] = False
            ret['comment'] = 'Types for "recurse" limited to "user", ' \
                             '"group" and "mode"'
        else:
            if 'user' in recurse:
                if user:
                    uid = __salt__['file.user_to_uid'](user)
                    # file.user_to_uid returns '' if user does not exist. Above
                    # check for user is not fatal, so we need to be sure user
                    # exists.
                    if isinstance(uid, string_types):
                        ret['result'] = False
                        ret['comment'] = 'Failed to enforce ownership for ' \
                                         'user {0} (user does not ' \
                                         'exist)'.format(user)
                else:
                    ret['result'] = False
                    ret['comment'] = 'user not specified, but configured as ' \
                                     'a target for recursive ownership ' \
                                     'management'
            else:
                user = None
            if 'group' in recurse:
                if group:
                    gid = __salt__['file.group_to_gid'](group)
                    # As above with user, we need to make sure group exists.
                    if isinstance(gid, string_types):
                        ret['result'] = False
                        ret['comment'] = 'Failed to enforce group ownership ' \
                                         'for group {0}'.format(group)
                else:
                    ret['result'] = False
                    ret['comment'] = 'group not specified, but configured ' \
                                     'as a target for recursive ownership ' \
                                     'management'
            else:
                group = None

            if 'mode' not in recurse:
                file_mode = None
                dir_mode = None

            for root, dirs, files in os.walk(name):
                for fn_ in files:
                    full = os.path.join(root, fn_)
                    ret, perms = __salt__['file.check_perms'](
                        full,
                        ret,
                        user,
                        group,
                        file_mode,
                        follow_symlinks)
                for dir_ in dirs:
                    full = os.path.join(root, dir_)
                    ret, perms = __salt__['file.check_perms'](
                        full,
                        ret,
                        user,
                        group,
                        dir_mode,
                        follow_symlinks)

    if clean:
        keep = _gen_keep_files(name, require)
        removed = _clean_dir(name, list(keep), exclude_pat)
        if removed:
            ret['changes']['removed'] = removed
            ret['comment'] = 'Files cleaned from directory {0}'.format(name)

    if not ret['comment']:
        ret['comment'] = 'Directory {0} updated'.format(name)

    if __opts__['test']:
        ret['comment'] = 'Directory {0} not updated'.format(name)
    elif not ret['changes'] and ret['result']:
        ret['comment'] = 'Directory {0} is in the correct state'.format(name)
    return ret