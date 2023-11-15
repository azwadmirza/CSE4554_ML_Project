def manage_file(name,
                sfn,
                ret,
                source,
                source_sum,
                user,
                group,
                mode,
                attrs,
                saltenv,
                backup,
                makedirs=False,
                template=None,   # pylint: disable=W0613
                show_changes=True,
                contents=None,
                dir_mode=None,
                follow_symlinks=True,
                skip_verify=False,
                keep_mode=False,
                encoding=None,
                encoding_errors='strict',
                **kwargs):
    '''
    Checks the destination against what was retrieved with get_managed and
    makes the appropriate modifications (if necessary).

    name
        location to place the file

    sfn
        location of cached file on the minion

        This is the path to the file stored on the minion. This file is placed
        on the minion using cp.cache_file.  If the hash sum of that file
        matches the source_sum, we do not transfer the file to the minion
        again.

        This file is then grabbed and if it has template set, it renders the
        file to be placed into the correct place on the system using
        salt.files.utils.copyfile()

    ret
        The initial state return data structure. Pass in ``None`` to use the
        default structure.

    source
        file reference on the master

    source_sum
        sum hash for source

    user
        user owner

    group
        group owner

    backup
        backup_mode

    attrs
        attributes to be set on file: '' means remove all of them

        .. versionadded:: 2018.3.0

    makedirs
        make directories if they do not exist

    template
        format of templating

    show_changes
        Include diff in state return

    contents:
        contents to be placed in the file

    dir_mode
        mode for directories created with makedirs

    skip_verify : False
        If ``True``, hash verification of remote file sources (``http://``,
        ``https://``, ``ftp://``) will be skipped, and the ``source_hash``
        argument will be ignored.

        .. versionadded:: 2016.3.0

    keep_mode : False
        If ``True``, and the ``source`` is a file from the Salt fileserver (or
        a local file on the minion), the mode of the destination file will be
        set to the mode of the source file.

        .. note:: keep_mode does not work with salt-ssh.

            As a consequence of how the files are transferred to the minion, and
            the inability to connect back to the master with salt-ssh, salt is
            unable to stat the file as it exists on the fileserver and thus
            cannot mirror the mode on the salt-ssh minion

    encoding
        If specified, then the specified encoding will be used. Otherwise, the
        file will be encoded using the system locale (usually UTF-8). See
        https://docs.python.org/3/library/codecs.html#standard-encodings for
        the list of available encodings.

        .. versionadded:: 2017.7.0

    encoding_errors : 'strict'
        Default is ```'strict'```.
        See https://docs.python.org/2/library/codecs.html#codec-base-classes
        for the error handling schemes.

        .. versionadded:: 2017.7.0

    CLI Example:

    .. code-block:: bash

        salt '*' file.manage_file /etc/httpd/conf.d/httpd.conf '' '{}' salt://http/httpd.conf '{hash_type: 'md5', 'hsum': <md5sum>}' root root '755' '' base ''

    .. versionchanged:: 2014.7.0
        ``follow_symlinks`` option added

    '''
    name = os.path.expanduser(name)

    if not ret:
        ret = {'name': name,
               'changes': {},
               'comment': '',
               'result': True}
    # Ensure that user-provided hash string is lowercase
    if source_sum and ('hsum' in source_sum):
        source_sum['hsum'] = source_sum['hsum'].lower()

    if source:
        if not sfn:
            # File is not present, cache it
            sfn = __salt__['cp.cache_file'](source, saltenv)
            if not sfn:
                return _error(
                    ret, 'Source file \'{0}\' not found'.format(source))
            htype = source_sum.get('hash_type', __opts__['hash_type'])
            # Recalculate source sum now that file has been cached
            source_sum = {
                'hash_type': htype,
                'hsum': get_hash(sfn, form=htype)
            }

        if keep_mode:
            if _urlparse(source).scheme in ('salt', 'file', ''):
                try:
                    mode = __salt__['cp.stat_file'](source, saltenv=saltenv, octal=True)
                except Exception as exc:
                    log.warning('Unable to stat %s: %s', sfn, exc)

    # Check changes if the target file exists
    if os.path.isfile(name) or os.path.islink(name):
        if os.path.islink(name) and follow_symlinks:
            real_name = os.path.realpath(name)
        else:
            real_name = name

        # Only test the checksums on files with managed contents
        if source and not (not follow_symlinks and os.path.islink(real_name)):
            name_sum = get_hash(real_name, source_sum.get('hash_type', __opts__['hash_type']))
        else:
            name_sum = None

        # Check if file needs to be replaced
        if source and (name_sum is None or source_sum.get('hsum', __opts__['hash_type']) != name_sum):
            if not sfn:
                sfn = __salt__['cp.cache_file'](source, saltenv)
            if not sfn:
                return _error(
                    ret, 'Source file \'{0}\' not found'.format(source))
            # If the downloaded file came from a non salt server or local
            # source, and we are not skipping checksum verification, then
            # verify that it matches the specified checksum.
            if not skip_verify \
                    and _urlparse(source).scheme != 'salt':
                dl_sum = get_hash(sfn, source_sum['hash_type'])
                if dl_sum != source_sum['hsum']:
                    ret['comment'] = (
                        'Specified {0} checksum for {1} ({2}) does not match '
                        'actual checksum ({3}). If the \'source_hash\' value '
                        'refers to a remote file with multiple possible '
                        'matches, then it may be necessary to set '
                        '\'source_hash_name\'.'.format(
                            source_sum['hash_type'],
                            source,
                            source_sum['hsum'],
                            dl_sum
                        )
                    )
                    ret['result'] = False
                    return ret

            # Print a diff equivalent to diff -u old new
            if __salt__['config.option']('obfuscate_templates'):
                ret['changes']['diff'] = '<Obfuscated Template>'
            elif not show_changes:
                ret['changes']['diff'] = '<show_changes=False>'
            else:
                try:
                    ret['changes']['diff'] = get_diff(
                        real_name, sfn, show_filenames=False)
                except CommandExecutionError as exc:
                    ret['changes']['diff'] = exc.strerror

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
            tmp = salt.utils.files.mkstemp(prefix=salt.utils.files.TEMPFILE_PREFIX,
                                           text=True)
            with salt.utils.files.fopen(tmp, 'wb') as tmp_:
                if encoding:
                    if salt.utils.platform.is_windows():
                        contents = os.linesep.join(
                            _splitlines_preserving_trailing_newline(contents))
                    log.debug('File will be encoded with %s', encoding)
                    tmp_.write(contents.encode(encoding=encoding, errors=encoding_errors))
                else:
                    tmp_.write(salt.utils.stringutils.to_bytes(contents))

            try:
                differences = get_diff(
                    real_name, tmp, show_filenames=False,
                    show_changes=show_changes, template=True)

            except CommandExecutionError as exc:
                ret.setdefault('warnings', []).append(
                    'Failed to detect changes to file: {0}'.format(exc.strerror)
                )
                differences = ''

            if differences:
                ret['changes']['diff'] = differences

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

        # Check for changing symlink to regular file here
        if os.path.islink(name) and not follow_symlinks:
            if not sfn:
                sfn = __salt__['cp.cache_file'](source, saltenv)
            if not sfn:
                return _error(
                    ret, 'Source file \'{0}\' not found'.format(source))
            # If the downloaded file came from a non salt server source verify
            # that it matches the intended sum value
            if not skip_verify and _urlparse(source).scheme != 'salt':
                dl_sum = get_hash(sfn, source_sum['hash_type'])
                if dl_sum != source_sum['hsum']:
                    ret['comment'] = (
                        'Specified {0} checksum for {1} ({2}) does not match '
                        'actual checksum ({3})'.format(
                            source_sum['hash_type'],
                            name,
                            source_sum['hsum'],
                            dl_sum
                        )
                    )
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

        if salt.utils.platform.is_windows():
            # This function resides in win_file.py and will be available
            # on Windows. The local function will be overridden
            # pylint: disable=E1120,E1121,E1123
            ret = check_perms(
                path=name,
                ret=ret,
                owner=kwargs.get('win_owner'),
                grant_perms=kwargs.get('win_perms'),
                deny_perms=kwargs.get('win_deny_perms'),
                inheritance=kwargs.get('win_inheritance', True),
                reset=kwargs.get('win_perms_reset', False))
            # pylint: enable=E1120,E1121,E1123
        else:
            ret, _ = check_perms(name, ret, user, group, mode, attrs, follow_symlinks)

        if ret['changes']:
            ret['comment'] = 'File {0} updated'.format(
                salt.utils.data.decode(name)
            )

        elif not ret['changes'] and ret['result']:
            ret['comment'] = 'File {0} is in the correct state'.format(
                salt.utils.data.decode(name)
            )
        if sfn:
            __clean_tmp(sfn)
        return ret
    else:  # target file does not exist
        contain_dir = os.path.dirname(name)

        def _set_mode_and_make_dirs(name, dir_mode, mode, user, group):
            # check for existence of windows drive letter
            if salt.utils.platform.is_windows():
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
                mode_list = [x for x in six.text_type(mode)][-3:]
                for idx in range(len(mode_list)):
                    if mode_list[idx] != '0':
                        mode_list[idx] = six.text_type(int(mode_list[idx]) | 1)
                dir_mode = ''.join(mode_list)

            if salt.utils.platform.is_windows():
                # This function resides in win_file.py and will be available
                # on Windows. The local function will be overridden
                # pylint: disable=E1120,E1121,E1123
                makedirs_(
                    path=name,
                    owner=kwargs.get('win_owner'),
                    grant_perms=kwargs.get('win_perms'),
                    deny_perms=kwargs.get('win_deny_perms'),
                    inheritance=kwargs.get('win_inheritance', True),
                    reset=kwargs.get('win_perms_reset', False))
                # pylint: enable=E1120,E1121,E1123
            else:
                makedirs_(name, user=user, group=group, mode=dir_mode)

        if source:
            # Apply the new file
            if not sfn:
                sfn = __salt__['cp.cache_file'](source, saltenv)
            if not sfn:
                return _error(
                    ret, 'Source file \'{0}\' not found'.format(source))
            # If the downloaded file came from a non salt server source verify
            # that it matches the intended sum value
            if not skip_verify \
                    and _urlparse(source).scheme != 'salt':
                dl_sum = get_hash(sfn, source_sum['hash_type'])
                if dl_sum != source_sum['hsum']:
                    ret['comment'] = (
                        'Specified {0} checksum for {1} ({2}) does not match '
                        'actual checksum ({3})'.format(
                            source_sum['hash_type'],
                            name,
                            source_sum['hsum'],
                            dl_sum
                        )
                    )
                    ret['result'] = False
                    return ret
            # It is a new file, set the diff accordingly
            ret['changes']['diff'] = 'New file'
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
            with salt.utils.files.set_umask(0o077 if mode else None):
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

        if contents is not None:
            # Write the static contents to a temporary file
            tmp = salt.utils.files.mkstemp(prefix=salt.utils.files.TEMPFILE_PREFIX,
                                           text=True)
            with salt.utils.files.fopen(tmp, 'wb') as tmp_:
                if encoding:
                    if salt.utils.platform.is_windows():
                        contents = os.linesep.join(
                            _splitlines_preserving_trailing_newline(contents))
                    log.debug('File will be encoded with %s', encoding)
                    tmp_.write(contents.encode(encoding=encoding, errors=encoding_errors))
                else:
                    tmp_.write(salt.utils.stringutils.to_bytes(contents))

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
        if mode is None and not salt.utils.platform.is_windows():
            # Get current umask
            mask = salt.utils.files.get_umask()
            # Calculate the mode value that results from the umask
            mode = oct((0o777 ^ mask) & 0o666)

        if salt.utils.platform.is_windows():
            # This function resides in win_file.py and will be available
            # on Windows. The local function will be overridden
            # pylint: disable=E1120,E1121,E1123
            ret = check_perms(
               path=name,
                ret=ret,
                owner=kwargs.get('win_owner'),
                grant_perms=kwargs.get('win_perms'),
                deny_perms=kwargs.get('win_deny_perms'),
                inheritance=kwargs.get('win_inheritance', True),
                reset=kwargs.get('win_perms_reset', False))
            # pylint: enable=E1120,E1121,E1123
        else:
            ret, _ = check_perms(name, ret, user, group, mode, attrs)

        if not ret['comment']:
            ret['comment'] = 'File ' + name + ' updated'

        if __opts__['test']:
            ret['comment'] = 'File ' + name + ' not updated'
        elif not ret['changes'] and ret['result']:
            ret['comment'] = 'File ' + name + ' is in the correct state'
        if sfn:
            __clean_tmp(sfn)

        return ret