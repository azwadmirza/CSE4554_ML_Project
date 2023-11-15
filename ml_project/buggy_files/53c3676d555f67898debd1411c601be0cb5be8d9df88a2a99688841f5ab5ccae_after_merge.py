def directory(name,
              user=None,
              group=None,
              recurse=None,
              max_depth=None,
              dir_mode=None,
              file_mode=None,
              makedirs=False,
              clean=False,
              require=None,
              exclude_pat=None,
              follow_symlinks=False,
              force=False,
              backupname=None,
              allow_symlink=True,
              children_only=False,
              win_owner=None,
              win_perms=None,
              win_deny_perms=None,
              win_inheritance=True,
              **kwargs):
    r'''
    Ensure that a named directory is present and has the right perms

    name
        The location to create or manage a directory, as an absolute path

    user
        The user to own the directory; this defaults to the user salt is
        running as on the minion

    group
        The group ownership set for the directory; this defaults to the group
        salt is running as on the minion. On Windows, this is ignored

    recurse
        Enforce user/group ownership and mode of directory recursively. Accepts
        a list of strings representing what you would like to recurse.  If
        ``mode`` is defined, will recurse on both ``file_mode`` and ``dir_mode`` if
        they are defined.  If ``ignore_files`` or ``ignore_dirs`` is included, files or
        directories will be left unchanged respectively.
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

        Leave files or directories unchanged:

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
                  - ignore_dirs

        .. versionadded:: 2015.5.0

    max_depth
        Limit the recursion depth. The default is no limit=None.
        'max_depth' and 'clean' are mutually exclusive.

        .. versionadded:: 2016.11.0

    dir_mode / mode
        The permissions mode to set any directories created. Not supported on
        Windows.

        The default mode for new files and directories corresponds umask of salt
        process. For existing files and directories it's not enforced.

    file_mode
        The permissions mode to set any files created if 'mode' is run in
        'recurse'. This defaults to dir_mode. Not supported on Windows.

        The default mode for new files and directories corresponds umask of salt
        process. For existing files and directories it's not enforced.

    makedirs
        If the directory is located in a path without a parent directory, then
        the state will fail. If makedirs is set to True, then the parent
        directories will be created to facilitate the creation of the named
        file.

    clean
        Make sure that only files that are set up by salt and required by this
        function are kept. If this option is set then everything in this
        directory will be deleted unless it is required.
        'clean' and 'max_depth' are mutually exclusive.

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

    allow_symlink : True
        If allow_symlink is True and the specified path is a symlink, it will be
        allowed to remain if it points to a directory. If allow_symlink is False
        then the state will fail, unless force is also set to True, in which case
        it will be removed or renamed, depending on the value of the backupname
        argument.

        .. versionadded:: 2014.7.0

    children_only : False
        If children_only is True the base of a path is excluded when performing
        a recursive operation. In case of /path/to/base, base will be ignored
        while all of /path/to/base/* are still operated on.

    win_owner : None
        The owner of the directory. If this is not passed, user will be used. If
        user is not passed, the account under which Salt is running will be
        used.

        .. versionadded:: 2017.7.0

    win_perms : None
        A dictionary containing permissions to grant and their propagation. For
        example: ``{'Administrators': {'perms': 'full_control', 'applies_to':
        'this_folder_only'}}`` Can be a single basic perm or a list of advanced
        perms. ``perms`` must be specified. ``applies_to`` is optional and
        defaults to ``this_folder_subfoler_files``.

        .. versionadded:: 2017.7.0

    win_deny_perms : None
        A dictionary containing permissions to deny and their propagation. For
        example: ``{'Administrators': {'perms': 'full_control', 'applies_to':
        'this_folder_only'}}`` Can be a single basic perm or a list of advanced
        perms.

        .. versionadded:: 2017.7.0

    win_inheritance : True
        True to inherit permissions from the parent directory, False not to
        inherit permission.

        .. versionadded:: 2017.7.0

    Here's an example using the above ``win_*`` parameters:

    .. code-block:: yaml

        create_config_dir:
          file.directory:
            - name: 'C:\config\'
            - win_owner: Administrators
            - win_perms:
                # Basic Permissions
                dev_ops:
                  perms: full_control
                # List of advanced permissions
                appuser:
                  perms:
                    - read_attributes
                    - read_ea
                    - create_folders
                    - read_permissions
                  applies_to: this_folder_only
                joe_snuffy:
                  perms: read
                  applies_to: this_folder_files
            - win_deny_perms:
                fred_snuffy:
                  perms: full_control
            - win_inheritance: False
    '''
    name = os.path.normcase(os.path.expanduser(name))
    ret = {'name': name,
           'changes': {},
           'pchanges': {},
           'result': True,
           'comment': ''}
    if not name:
        return _error(ret, 'Must provide name to file.directory')
    # Remove trailing slash, if present and we're not working on "/" itself
    if name[-1] == '/' and name != '/':
        name = name[:-1]

    if max_depth is not None and clean:
        return _error(ret, 'Cannot specify both max_depth and clean')

    user = _test_owner(kwargs, user=user)
    if salt.utils.is_windows():

        # If win_owner not passed, use user
        if win_owner is None:
            win_owner = user if user else salt.utils.win_functions.get_current_user()

        # Group isn't relevant to Windows, use win_perms/win_deny_perms
        if group is not None:
            log.warning(
                'The group argument for {0} has been ignored as this is '
                'a Windows system. Please use the `win_*` parameters to set '
                'permissions in Windows.'.format(name)
            )
        group = user

    if 'mode' in kwargs and not dir_mode:
        dir_mode = kwargs.get('mode', [])

    if not file_mode:
        file_mode = dir_mode

    # Make sure that leading zeros stripped by YAML loader are added back
    dir_mode = salt.utils.normalize_mode(dir_mode)
    file_mode = salt.utils.normalize_mode(file_mode)

    if salt.utils.is_windows():
        # Verify win_owner is valid on the target system
        try:
            salt.utils.win_dacl.get_sid(win_owner)
        except CommandExecutionError as exc:
            return _error(ret, exc)
    else:
        # Verify user and group are valid
        u_check = _check_user(user, group)
        if u_check:
            # The specified user or group do not exist
            return _error(ret, u_check)

    # Must be an absolute path
    if not os.path.isabs(name):
        return _error(
            ret, 'Specified file {0} is not an absolute path'.format(name))

    # Check for existing file or symlink
    if os.path.isfile(name) or (not allow_symlink and os.path.islink(name)) \
       or (force and os.path.islink(name)):
        # Was a backupname specified
        if backupname is not None:
            # Make a backup first
            if os.path.lexists(backupname):
                if not force:
                    return _error(ret, ((
                                            'File exists where the backup target {0} should go'
                                        ).format(backupname)))
                else:
                    __salt__['file.remove'](backupname)
            os.rename(name, backupname)
        elif force:
            # Remove whatever is in the way
            if os.path.isfile(name):
                os.remove(name)
                ret['changes']['forced'] = 'File was forcibly replaced'
            elif __salt__['file.is_link'](name):
                __salt__['file.remove'](name)
                ret['changes']['forced'] = 'Symlink was forcibly replaced'
            else:
                __salt__['file.remove'](name)
        else:
            if os.path.isfile(name):
                return _error(
                    ret,
                    'Specified location {0} exists and is a file'.format(name))
            elif os.path.islink(name):
                return _error(
                    ret,
                    'Specified location {0} exists and is a symlink'.format(name))

    # Check directory?
    if salt.utils.is_windows():
        presult, pcomment, ret['pchanges'] = _check_directory_win(
            name, win_owner, win_perms, win_deny_perms, win_inheritance)
    else:
        presult, pcomment, ret['pchanges'] = _check_directory(
            name, user, group, recurse or [], dir_mode, clean, require,
            exclude_pat, max_depth, follow_symlinks)

    if __opts__['test']:
        ret['result'] = presult
        ret['comment'] = pcomment
        ret['changes'] = ret['pchanges']
        return ret

    if not os.path.isdir(name):
        # The dir does not exist, make it
        if not os.path.isdir(os.path.dirname(name)):
            # The parent directory does not exist, create them
            if makedirs:
                # Everything's good, create the parent Dirs
                try:
                    _makedirs(name=name,
                              user=user,
                              group=group,
                              dir_mode=dir_mode,
                              win_owner=win_owner,
                              win_perms=win_perms,
                              win_deny_perms=win_deny_perms,
                              win_inheritance=win_inheritance)
                except CommandExecutionError as exc:
                    return _error(ret, 'Drive {0} is not mapped'.format(exc.message))
            else:
                return _error(
                    ret, 'No directory to create {0} in'.format(name))

        if salt.utils.is_windows():
            __salt__['file.mkdir'](name, win_owner, win_perms, win_deny_perms,
                                   win_inheritance)
        else:
            __salt__['file.mkdir'](name, user=user, group=group, mode=dir_mode)

        ret['changes'][name] = 'New Dir'

    if not os.path.isdir(name):
        return _error(ret, 'Failed to create directory {0}'.format(name))

    # issue 32707: skip this __salt__['file.check_perms'] call if children_only == True
    # Check permissions
    if not children_only:
        if salt.utils.is_windows():
            ret = __salt__['file.check_perms'](
                name, ret, win_owner, win_perms, win_deny_perms, win_inheritance)
        else:
            ret, perms = __salt__['file.check_perms'](
                name, ret, user, group, dir_mode, follow_symlinks)

    errors = []
    if recurse or clean:
        # walk path only once and store the result
        walk_l = list(_depth_limited_walk(name, max_depth))
        # root: (dirs, files) structure, compatible for python2.6
        walk_d = {}
        for i in walk_l:
            walk_d[i[0]] = (i[1], i[2])

    recurse_set = None
    if recurse:
        try:
            recurse_set = _get_recurse_set(recurse)
        except (TypeError, ValueError) as exc:
            ret['result'] = False
            ret['comment'] = '{0}'.format(exc)
            # NOTE: Should this be enough to stop the whole check altogether?
    if recurse_set:
        if 'user' in recurse_set:
            if user:
                uid = __salt__['file.user_to_uid'](user)
                # file.user_to_uid returns '' if user does not exist. Above
                # check for user is not fatal, so we need to be sure user
                # exists.
                if isinstance(uid, six.string_types):
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
        if 'group' in recurse_set:
            if group:
                gid = __salt__['file.group_to_gid'](group)
                # As above with user, we need to make sure group exists.
                if isinstance(gid, six.string_types):
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

        if 'mode' not in recurse_set:
            file_mode = None
            dir_mode = None

        check_files = 'ignore_files' not in recurse_set
        check_dirs = 'ignore_dirs' not in recurse_set

        for root, dirs, files in walk_l:
            if check_files:
                for fn_ in files:
                    full = os.path.join(root, fn_)
                    try:
                        if salt.utils.is_windows():
                            ret = __salt__['file.check_perms'](
                                full, ret, win_owner, win_perms, win_deny_perms,
                                win_inheritance)
                        else:
                            ret, _ = __salt__['file.check_perms'](
                                full, ret, user, group, file_mode, follow_symlinks)
                    except CommandExecutionError as exc:
                        if not exc.strerror.startswith('Path not found'):
                            errors.append(exc.strerror)

            if check_dirs:
                for dir_ in dirs:
                    full = os.path.join(root, dir_)
                    try:
                        if salt.utils.is_windows():
                            ret = __salt__['file.check_perms'](
                                full, ret, win_owner, win_perms, win_deny_perms,
                                win_inheritance)
                        else:
                            ret, _ = __salt__['file.check_perms'](
                                full, ret, user, group, dir_mode, follow_symlinks)
                    except CommandExecutionError as exc:
                        if not exc.strerror.startswith('Path not found'):
                            errors.append(exc.strerror)

    if clean:
        keep = _gen_keep_files(name, require, walk_d)
        log.debug('List of kept files when use file.directory with clean: %s',
                  keep)
        removed = _clean_dir(name, list(keep), exclude_pat)
        if removed:
            ret['changes']['removed'] = removed
            ret['comment'] = 'Files cleaned from directory {0}'.format(name)

    # issue 32707: reflect children_only selection in comments
    if not ret['comment']:
        if children_only:
            ret['comment'] = 'Directory {0}/* updated'.format(name)
        else:
            ret['comment'] = 'Directory {0} updated'.format(name)

    if __opts__['test']:
        ret['comment'] = 'Directory {0} not updated'.format(name)
    elif not ret['changes'] and ret['result']:
        orig_comment = None
        if ret['comment']:
            orig_comment = ret['comment']

        ret['comment'] = 'Directory {0} is in the correct state'.format(name)
        if orig_comment:
            ret['comment'] = '\n'.join([ret['comment'], orig_comment])

    if errors:
        ret['result'] = False
        ret['comment'] += '\n\nThe following errors were encountered:\n'
        for error in errors:
            ret['comment'] += '\n- {0}'.format(error)

    return ret