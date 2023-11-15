def manage_file(name,
                sfn,
                ret,
                source,
                source_sum,
                user,
                group,
                mode,
                saltenv,
                backup,
                makedirs=False,
                template=None,   # pylint: disable=W0613
                show_diff=True,
                contents=None,
                dir_mode=None,
                follow_symlinks=True):
    '''
    Checks the destination against what was retrieved with get_managed and
    makes the appropriate modifications (if necessary).

    name
        location to place the file

    sfn
        location of cached file on the minion

        This is the path to the file stored on the minion. This file is placed on the minion
        using cp.cache_file.  If the hash sum of that file matches the source_sum, we do not
        transfer the file to the minion again.

        This file is then grabbed and if it has template set, it renders the file to be placed
        into the correct place on the system using salt.files.utils.copyfile()

    ret
        The initial state return data structure. Pass in ``None`` to use the default structure.

    source
        file reference on the master

    source_hash
        sum hash for source

    user
        user owner

    group
        group owner

    backup
        backup_mode

    makedirs
        make directories if they do not exist

    template
        format of templating

    show_diff
        Include diff in state return

    contents:
        contents to be placed in the file

    dir_mode
        mode for directories created with makedirs

    CLI Example:

    .. code-block:: bash

        salt '*' file.manage_file /etc/httpd/conf.d/httpd.conf '' '{}' salt://http/httpd.conf '{hash_type: 'md5', 'hsum': <md5sum>}' root root '755' base ''

    .. versionchanged:: 2014.7.0
        ``follow_symlinks`` option added

    '''
    name = os.path.expanduser(name)

    if not ret:
        ret = {'name': name,
               'changes': {},
               'comment': '',
               'result': True}

    # Check changes if the target file exists
    if os.path.isfile(name) or os.path.islink(name):
        if os.path.islink(name) and follow_symlinks:
            real_name = os.path.realpath(name)
        else:
            real_name = name

        # Only test the checksums on files with managed contents
        if source and not (not follow_symlinks and os.path.islink(real_name)):
            name_sum = get_hash(real_name, source_sum['hash_type'])
        else:
            name_sum = None

        # Check if file needs to be replaced
        if source and (source_sum['hsum'] != name_sum or name_sum is None):
            if not sfn:
                sfn = __salt__['cp.cache_file'](source, saltenv)
            if not sfn:
                return _error(
                    ret, 'Source file {0!r} not found'.format(source))
            # If the downloaded file came from a non salt server source verify
            # that it matches the intended sum value
            if _urlparse(source).scheme != 'salt':
                dl_sum = get_hash(sfn, source_sum['hash_type'])
                if dl_sum != source_sum['hsum']:
                    ret['comment'] = ('File sum set for file {0} of {1} does '
                                      'not match real sum of {2}'
                                      ).format(name,
                                               source_sum['hsum'],
                                               dl_sum)
                    ret['result'] = False
                    return ret

            # Print a diff equivalent to diff -u old new
            if __salt__['config.option']('obfuscate_templates'):
                ret['changes']['diff'] = '<Obfuscated Template>'
            elif not show_diff:
                ret['changes']['diff'] = '<show_diff=False>'
            else:
                # Check to see if the files are bins
                bdiff = _binary_replace(real_name, sfn)
                if bdiff:
                    ret['changes']['diff'] = bdiff
                else:
                    with contextlib.nested(
                            salt.utils.fopen(sfn, 'r'),
                            salt.utils.fopen(real_name, 'r')) as (src, name_):
                        slines = src.readlines()
                        nlines = name_.readlines()

                    sndiff = ''.join(difflib.unified_diff(nlines, slines))
                    if sndiff:
                        ret['changes']['diff'] = sndiff

            # Pre requisites are met, and the file needs to be replaced, do it
            try:
                salt.utils.files.copyfile(sfn,
                                    real_name,
                                    __salt__['config.backup_mode'](backup),
                                    __opts__['cachedir'])
            except IOError as io_error:
                __clean_tmp(sfn)
                return _error(
                    ret, 'Failed to commit change: {0}'.format(io_error))

        if contents is not None:
            # Write the static contents to a temporary file
            tmp = salt.utils.mkstemp(text=True)
            with salt.utils.fopen(tmp, 'w') as tmp_:
                tmp_.write(str(contents))

            # Compare contents of files to know if we need to replace
            with contextlib.nested(
                    salt.utils.fopen(tmp, 'r'),
                    salt.utils.fopen(real_name, 'r')) as (src, name_):
                slines = src.readlines()
                nlines = name_.readlines()
                different = ''.join(slines) != ''.join(nlines)

            if different:
                if __salt__['config.option']('obfuscate_templates'):
                    ret['changes']['diff'] = '<Obfuscated Template>'
                elif not show_diff:
                    ret['changes']['diff'] = '<show_diff=False>'
                else:
                    if salt.utils.istextfile(real_name):
                        ret['changes']['diff'] = \
                            ''.join(difflib.unified_diff(nlines, slines))
                    else:
                        ret['changes']['diff'] = \
                            'Replace binary file with text file'

                # Pre requisites are met, the file needs to be replaced, do it
                try:
                    salt.utils.files.copyfile(tmp,
                                        real_name,
                                        __salt__['config.backup_mode'](backup),
                                        __opts__['cachedir'])
                except IOError as io_error:
                    __clean_tmp(tmp)
                    return _error(
                        ret, 'Failed to commit change: {0}'.format(io_error))
            __clean_tmp(tmp)

        # check for changing symlink to regular file here
        if os.path.islink(name) and not follow_symlinks:
            if not sfn:
                sfn = __salt__['cp.cache_file'](source, saltenv)
            if not sfn:
                return _error(
                    ret, 'Source file {0!r} not found'.format(source))
            # If the downloaded file came from a non salt server source verify
            # that it matches the intended sum value
            if _urlparse(source).scheme != 'salt':
                dl_sum = get_hash(sfn, source_sum['hash_type'])
                if dl_sum != source_sum['hsum']:
                    ret['comment'] = ('File sum set for file {0} of {1} does '
                                      'not match real sum of {2}'
                                      ).format(name,
                                               source_sum['hsum'],
                                               dl_sum)
                    ret['result'] = False
                    return ret

            try:
                salt.utils.files.copyfile(sfn,
                                    name,
                                    __salt__['config.backup_mode'](backup),
                                    __opts__['cachedir'])
            except IOError as io_error:
                __clean_tmp(sfn)
                return _error(
                    ret, 'Failed to commit change: {0}'.format(io_error))

            ret['changes']['diff'] = \
                'Replace symbolic link with regular file'

        ret, _ = check_perms(name, ret, user, group, mode, follow_symlinks)

        if ret['changes']:
            ret['comment'] = 'File {0} updated'.format(name)

        elif not ret['changes'] and ret['result']:
            ret['comment'] = u'File {0} is in the correct state'.format(name)
        if sfn:
            __clean_tmp(sfn)
        return ret
    else:  # target file does not exist
        contain_dir = os.path.dirname(name)

        def _set_mode_and_make_dirs(name, dir_mode, mode, user, group):
            # check for existence of windows drive letter
            if salt.utils.is_windows():
                drive, _ = os.path.splitdrive(name)
                if drive and not os.path.exists(drive):
                    __clean_tmp(sfn)
                    return _error(ret,
                                  '{0} drive not present'.format(drive))
            if dir_mode is None and mode is not None:
                # Add execute bit to each nonzero digit in the mode, if
                # dir_mode was not specified. Otherwise, any
                # directories created with makedirs_() below can't be
                # listed via a shell.
                mode_list = [x for x in str(mode)][-3:]
                for idx in range(len(mode_list)):
                    if mode_list[idx] != '0':
                        mode_list[idx] = str(int(mode_list[idx]) | 1)
                dir_mode = ''.join(mode_list)
            makedirs_(name, user=user,
                      group=group, mode=dir_mode)

        if source:
            # It is a new file, set the diff accordingly
            ret['changes']['diff'] = 'New file'
            # Apply the new file
            if not sfn:
                sfn = __salt__['cp.cache_file'](source, saltenv)
            if not sfn:
                return _error(
                    ret, 'Source file {0!r} not found'.format(source))
            # If the downloaded file came from a non salt server source verify
            # that it matches the intended sum value
            if _urlparse(source).scheme != 'salt':
                dl_sum = get_hash(sfn, source_sum['hash_type'])
                if dl_sum != source_sum['hsum']:
                    ret['comment'] = ('File sum set for file {0} of {1} does '
                                      'not match real sum of {2}'
                                      ).format(name,
                                               source_sum['hsum'],
                                               dl_sum)
                    ret['result'] = False
                    return ret
            if not os.path.isdir(contain_dir):
                if makedirs:
                    _set_mode_and_make_dirs(name, dir_mode, mode, user, group)
                else:
                    __clean_tmp(sfn)
                    # No changes actually made
                    ret['changes'].pop('diff', None)
                    return _error(ret, 'Parent directory not present')
        else:  # source != True
            if not os.path.isdir(contain_dir):
                if makedirs:
                    _set_mode_and_make_dirs(name, dir_mode, mode, user, group)
                else:
                    __clean_tmp(sfn)
                    # No changes actually made
                    ret['changes'].pop('diff', None)
                    return _error(ret, 'Parent directory not present')

            # Create the file, user rw-only if mode will be set to prevent
            # a small security race problem before the permissions are set
            if mode:
                current_umask = os.umask(0o77)

            # Create a new file when test is False and source is None
            if contents is None:
                if not __opts__['test']:
                    if touch(name):
                        ret['changes']['new'] = 'file {0} created'.format(name)
                        ret['comment'] = 'Empty file'
                    else:
                        return _error(
                            ret, 'Empty file {0} not created'.format(name)
                        )
            else:
                if not __opts__['test']:
                    if touch(name):
                        ret['changes']['diff'] = 'New file'
                    else:
                        return _error(
                            ret, 'File {0} not created'.format(name)
                        )

            if mode:
                os.umask(current_umask)

        if contents is not None:
            # Write the static contents to a temporary file
            tmp = salt.utils.mkstemp(text=True)
            with salt.utils.fopen(tmp, 'w') as tmp_:
                tmp_.write(str(contents))
            # Copy into place
            salt.utils.files.copyfile(tmp,
                                name,
                                __salt__['config.backup_mode'](backup),
                                __opts__['cachedir'])
            __clean_tmp(tmp)
        # Now copy the file contents if there is a source file
        elif sfn:
            salt.utils.files.copyfile(sfn,
                                name,
                                __salt__['config.backup_mode'](backup),
                                __opts__['cachedir'])
            __clean_tmp(sfn)

        # This is a new file, if no mode specified, use the umask to figure
        # out what mode to use for the new file.
        if mode is None and not salt.utils.is_windows():
            # Get current umask
            mask = os.umask(0)
            os.umask(mask)
            # Calculate the mode value that results from the umask
            mode = oct((0o777 ^ mask) & 0o666)
        ret, _ = check_perms(name, ret, user, group, mode)

        if not ret['comment']:
            ret['comment'] = 'File ' + name + ' updated'

        if __opts__['test']:
            ret['comment'] = 'File ' + name + ' not updated'
        elif not ret['changes'] and ret['result']:
            ret['comment'] = 'File ' + name + ' is in the correct state'
        if sfn:
            __clean_tmp(sfn)
        return ret