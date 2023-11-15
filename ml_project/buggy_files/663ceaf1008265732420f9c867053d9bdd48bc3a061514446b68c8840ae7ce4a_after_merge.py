def replace(path,
            pattern,
            repl,
            count=0,
            flags=8,
            bufsize=1,
            append_if_not_found=False,
            prepend_if_not_found=False,
            not_found_content=None,
            backup='.bak',
            dry_run=False,
            search_only=False,
            show_changes=True,
            ignore_if_missing=False,
            preserve_inode=True,
        ):
    '''
    .. versionadded:: 0.17.0

    Replace occurrences of a pattern in a file. If ``show_changes`` is
    ``True``, then a diff of what changed will be returned, otherwise a
    ``True`` will be returned when changes are made, and ``False`` when
    no changes are made.

    This is a pure Python implementation that wraps Python's :py:func:`~re.sub`.

    path
        Filesystem path to the file to be edited. If a symlink is specified, it
        will be resolved to its target.

    pattern
        A regular expression, to be matched using Python's
        :py:func:`~re.search`.

    repl
        The replacement text

    count : 0
        Maximum number of pattern occurrences to be replaced. If count is a
        positive integer ``n``, only ``n`` occurrences will be replaced,
        otherwise all occurrences will be replaced.

    flags (list or int)
        A list of flags defined in the :ref:`re module documentation
        <contents-of-module-re>`. Each list item should be a string that will
        correlate to the human-friendly flag name. E.g., ``['IGNORECASE',
        'MULTILINE']``. Optionally, ``flags`` may be an int, with a value
        corresponding to the XOR (``|``) of all the desired flags. Defaults to
        8 (which supports 'MULTILINE').

    bufsize (int or str)
        How much of the file to buffer into memory at once. The
        default value ``1`` processes one line at a time. The special value
        ``file`` may be specified which will read the entire file into memory
        before processing.

    append_if_not_found : False
        .. versionadded:: 2014.7.0

        If set to ``True``, and pattern is not found, then the content will be
        appended to the file.

    prepend_if_not_found : False
        .. versionadded:: 2014.7.0

        If set to ``True`` and pattern is not found, then the content will be
        prepended to the file.

    not_found_content
        .. versionadded:: 2014.7.0

        Content to use for append/prepend if not found. If None (default), uses
        ``repl``. Useful when ``repl`` uses references to group in pattern.

    backup : .bak
        The file extension to use for a backup of the file before editing. Set
        to ``False`` to skip making a backup.

    dry_run : False
        If set to ``True``, no changes will be made to the file, the function
        will just return the changes that would have been made (or a
        ``True``/``False`` value if ``show_changes`` is set to ``False``).

    search_only : False
        If set to true, this no changes will be performed on the file, and this
        function will simply return ``True`` if the pattern was matched, and
        ``False`` if not.

    show_changes : True
        If ``True``, return a diff of changes made. Otherwise, return ``True``
        if changes were made, and ``False`` if not.

        .. note::
            Using this option will store two copies of the file in memory (the
            original version and the edited version) in order to generate the
            diff. This may not normally be a concern, but could impact
            performance if used with large files.

    ignore_if_missing : False
        .. versionadded:: 2015.8.0

        If set to ``True``, this function will simply return ``False``
        if the file doesn't exist. Otherwise, an error will be thrown.

    preserve_inode : True
        .. versionadded:: 2015.8.0

        Preserve the inode of the file, so that any hard links continue to
        share the inode with the original filename. This works by *copying* the
        file, reading from the copy, and writing to the file at the original
        inode. If ``False``, the file will be *moved* rather than copied, and a
        new file will be written to a new inode, but using the original
        filename. Hard links will then share an inode with the backup, instead
        (if using ``backup`` to create a backup copy).

    If an equal sign (``=``) appears in an argument to a Salt command it is
    interpreted as a keyword argument in the format ``key=val``. That
    processing can be bypassed in order to pass an equal sign through to the
    remote shell command by manually specifying the kwarg:

    .. code-block:: bash

        salt '*' file.replace /path/to/file pattern='=' repl=':'
        salt '*' file.replace /path/to/file pattern="bind-address\\s*=" repl='bind-address:'

    CLI Examples:

    .. code-block:: bash

        salt '*' file.replace /etc/httpd/httpd.conf pattern='LogLevel warn' repl='LogLevel info'
        salt '*' file.replace /some/file pattern='before' repl='after' flags='[MULTILINE, IGNORECASE]'
    '''
    symlink = False
    if is_link(path):
        symlink = True
        target_path = os.readlink(path)
        given_path = os.path.expanduser(path)

    path = os.path.realpath(os.path.expanduser(path))

    if not os.path.exists(path):
        if ignore_if_missing:
            return False
        else:
            raise SaltInvocationError('File not found: {0}'.format(path))

    if not salt.utils.istextfile(path):
        raise SaltInvocationError(
            'Cannot perform string replacements on a binary file: {0}'
            .format(path)
        )

    if search_only and (append_if_not_found or prepend_if_not_found):
        raise SaltInvocationError(
            'search_only cannot be used with append/prepend_if_not_found'
        )

    if append_if_not_found and prepend_if_not_found:
        raise SaltInvocationError(
            'Only one of append and prepend_if_not_found is permitted'
        )

    flags_num = _get_flags(flags)
    cpattern = re.compile(salt.utils.to_bytes(pattern), flags_num)
    filesize = os.path.getsize(path)
    if bufsize == 'file':
        bufsize = filesize

    # Search the file; track if any changes have been made for the return val
    has_changes = False
    orig_file = []  # used if show_changes
    new_file = []  # used if show_changes
    if not salt.utils.is_windows():
        pre_user = get_user(path)
        pre_group = get_group(path)
        pre_mode = salt.utils.normalize_mode(get_mode(path))

    # Avoid TypeErrors by forcing repl to be bytearray related to mmap
    # Replacement text may contains integer: 123 for example
    repl = salt.utils.to_bytes(str(repl))
    if not_found_content:
        not_found_content = salt.utils.to_bytes(not_found_content)

    found = False
    temp_file = None
    content = salt.utils.to_str(not_found_content) if not_found_content and \
                                       (prepend_if_not_found or
                                        append_if_not_found) \
                                     else salt.utils.to_str(repl)

    try:
        # First check the whole file, determine whether to make the replacement
        # Searching first avoids modifying the time stamp if there are no changes
        r_data = None
        # Use a read-only handle to open the file
        with salt.utils.fopen(path,
                              mode='rb',
                              buffering=bufsize) as r_file:
            try:
                # mmap throws a ValueError if the file is empty.
                r_data = mmap.mmap(r_file.fileno(),
                                   0,
                                   access=mmap.ACCESS_READ)
            except (ValueError, mmap.error):
                # size of file in /proc is 0, but contains data
                r_data = salt.utils.to_bytes("".join(r_file))
            if search_only:
                # Just search; bail as early as a match is found
                if re.search(cpattern, r_data):
                    return True  # `with` block handles file closure
            else:
                result, nrepl = re.subn(cpattern, repl, r_data, count)

                # found anything? (even if no change)
                if nrepl > 0:
                    found = True
                    # Identity check the potential change
                    has_changes = True if pattern != repl else has_changes

                if prepend_if_not_found or append_if_not_found:
                    # Search for content, to avoid pre/appending the
                    # content if it was pre/appended in a previous run.
                    if re.search(salt.utils.to_bytes('^{0}$'.format(re.escape(content))),
                                 r_data,
                                 flags=flags_num):
                        # Content was found, so set found.
                        found = True

                # Keep track of show_changes here, in case the file isn't
                # modified
                if show_changes or append_if_not_found or \
                   prepend_if_not_found:
                    orig_file = r_data.read(filesize).splitlines(True) \
                        if isinstance(r_data, mmap.mmap) \
                        else r_data.splitlines(True)
                    new_file = result.splitlines(True)

    except (OSError, IOError) as exc:
        raise CommandExecutionError(
            "Unable to open file '{0}'. "
            "Exception: {1}".format(path, exc)
            )
    finally:
        if r_data and isinstance(r_data, mmap.mmap):
            r_data.close()

    if has_changes and not dry_run:
        # Write the replacement text in this block.
        try:
            # Create a copy to read from and to use as a backup later
            temp_file = _mkstemp_copy(path=path,
                                      preserve_inode=preserve_inode)
        except (OSError, IOError) as exc:
            raise CommandExecutionError("Exception: {0}".format(exc))

        r_data = None
        try:
            # Open the file in write mode
            with salt.utils.fopen(path,
                        mode='w',
                        buffering=bufsize) as w_file:
                try:
                    # Open the temp file in read mode
                    with salt.utils.fopen(temp_file,
                                          mode='r',
                                          buffering=bufsize) as r_file:
                        r_data = mmap.mmap(r_file.fileno(),
                                           0,
                                           access=mmap.ACCESS_READ)
                        result, nrepl = re.subn(cpattern, repl,
                                                r_data, count)
                        try:
                            w_file.write(salt.utils.to_str(result))
                        except (OSError, IOError) as exc:
                            raise CommandExecutionError(
                                "Unable to write file '{0}'. Contents may "
                                "be truncated. Temporary file contains copy "
                                "at '{1}'. "
                                "Exception: {2}".format(path, temp_file, exc)
                                )
                except (OSError, IOError) as exc:
                    raise CommandExecutionError("Exception: {0}".format(exc))
                finally:
                    if r_data and isinstance(r_data, mmap.mmap):
                        r_data.close()
        except (OSError, IOError) as exc:
            raise CommandExecutionError("Exception: {0}".format(exc))

    if not found and (append_if_not_found or prepend_if_not_found):
        if not_found_content is None:
            not_found_content = repl
        if prepend_if_not_found:
            new_file.insert(0, not_found_content + b'\n')
        else:
            # append_if_not_found
            # Make sure we have a newline at the end of the file
            if 0 != len(new_file):
                if not new_file[-1].endswith(b'\n'):
                    new_file[-1] += b'\n'
            new_file.append(not_found_content + b'\n')
        has_changes = True
        if not dry_run:
            try:
                # Create a copy to read from and for later use as a backup
                temp_file = _mkstemp_copy(path=path,
                                          preserve_inode=preserve_inode)
            except (OSError, IOError) as exc:
                raise CommandExecutionError("Exception: {0}".format(exc))
            # write new content in the file while avoiding partial reads
            try:
                fh_ = salt.utils.atomicfile.atomic_open(path, 'w')
                for line in new_file:
                    fh_.write(salt.utils.to_str(line))
            finally:
                fh_.close()

    if backup and has_changes and not dry_run:
        # keep the backup only if it was requested
        # and only if there were any changes
        backup_name = '{0}{1}'.format(path, backup)
        try:
            shutil.move(temp_file, backup_name)
        except (OSError, IOError) as exc:
            raise CommandExecutionError(
                "Unable to move the temp file '{0}' to the "
                "backup file '{1}'. "
                "Exception: {2}".format(path, temp_file, exc)
                )
        if symlink:
            symlink_backup = '{0}{1}'.format(given_path, backup)
            target_backup = '{0}{1}'.format(target_path, backup)
            # Always clobber any existing symlink backup
            # to match the behaviour of the 'backup' option
            try:
                os.symlink(target_backup, symlink_backup)
            except OSError:
                os.remove(symlink_backup)
                os.symlink(target_backup, symlink_backup)
            except:
                raise CommandExecutionError(
                    "Unable create backup symlink '{0}'. "
                    "Target was '{1}'. "
                    "Exception: {2}".format(symlink_backup, target_backup,
                                            exc)
                    )
    elif temp_file:
        try:
            os.remove(temp_file)
        except (OSError, IOError) as exc:
            raise CommandExecutionError(
                "Unable to delete temp file '{0}'. "
                "Exception: {1}".format(temp_file, exc)
                )

    if not dry_run and not salt.utils.is_windows():
        check_perms(path, None, pre_user, pre_group, pre_mode)

    if show_changes:
        orig_file_as_str = ''.join([salt.utils.to_str(x) for x in orig_file])
        new_file_as_str = ''.join([salt.utils.to_str(x) for x in new_file])
        return ''.join(difflib.unified_diff(orig_file_as_str, new_file_as_str))

    return has_changes