def get_diff(file1,
             file2,
             saltenv='base',
             show_filenames=True,
             show_changes=True,
             template=False,
             source_hash_file1=None,
             source_hash_file2=None):
    '''
    Return unified diff of two files

    file1
        The first file to feed into the diff utility

        .. versionchanged:: 2018.3.0
            Can now be either a local or remote file. In earlier releases,
            thuis had to be a file local to the minion.

    file2
        The second file to feed into the diff utility

        .. versionchanged:: 2018.3.0
            Can now be either a local or remote file. In earlier releases, this
            had to be a file on the salt fileserver (i.e.
            ``salt://somefile.txt``)

    show_filenames : True
        Set to ``False`` to hide the filenames in the top two lines of the
        diff.

    show_changes : True
        If set to ``False``, and there are differences, then instead of a diff
        a simple message stating that show_changes is set to ``False`` will be
        returned.

    template : False
        Set to ``True`` if two templates are being compared. This is not useful
        except for within states, with the ``obfuscate_templates`` option set
        to ``True``.

        .. versionadded:: 2018.3.0

    source_hash_file1
        If ``file1`` is an http(s)/ftp URL and the file exists in the minion's
        file cache, this option can be passed to keep the minion from
        re-downloading the archive if the cached copy matches the specified
        hash.

        .. versionadded:: 2018.3.0

    source_hash_file2
        If ``file2`` is an http(s)/ftp URL and the file exists in the minion's
        file cache, this option can be passed to keep the minion from
        re-downloading the archive if the cached copy matches the specified
        hash.

        .. versionadded:: 2018.3.0

    CLI Examples:

    .. code-block:: bash

        salt '*' file.get_diff /home/fred/.vimrc salt://users/fred/.vimrc
        salt '*' file.get_diff /tmp/foo.txt /tmp/bar.txt
    '''
    files = (file1, file2)
    source_hashes = (source_hash_file1, source_hash_file2)
    paths = []
    errors = []

    for filename, source_hash in zip(files, source_hashes):
        try:
            # Local file paths will just return the same path back when passed
            # to cp.cache_file.
            cached_path = __salt__['cp.cache_file'](filename,
                                                    saltenv,
                                                    source_hash=source_hash)
            if cached_path is False:
                errors.append(
                    'File {0} not found'.format(
                        salt.utils.stringutils.to_unicode(filename)
                    )
                )
                continue
            paths.append(cached_path)
        except MinionError as exc:
            errors.append(salt.utils.stringutils.to_unicode(exc.__str__()))
            continue

    if errors:
        raise CommandExecutionError(
            'Failed to cache one or more files',
            info=errors
        )

    args = []
    for filename in paths:
        try:
            with salt.utils.files.fopen(filename, 'rb') as fp_:
                args.append(fp_.readlines())
        except (IOError, OSError) as exc:
            raise CommandExecutionError(
                'Failed to read {0}: {1}'.format(
                    salt.utils.stringutils.to_unicode(filename),
                    exc.strerror
                )
            )

    if args[0] != args[1]:
        if template and __salt__['config.option']('obfuscate_templates'):
            ret = '<Obfuscated Template>'
        elif not show_changes:
            ret = '<show_changes=False>'
        else:
            bdiff = _binary_replace(*paths)  # pylint: disable=no-value-for-parameter
            if bdiff:
                ret = bdiff
            else:
                if show_filenames:
                    args.extend(paths)
                ret = __utils__['stringutils.get_diff'](*args)
        return ret
    return ''