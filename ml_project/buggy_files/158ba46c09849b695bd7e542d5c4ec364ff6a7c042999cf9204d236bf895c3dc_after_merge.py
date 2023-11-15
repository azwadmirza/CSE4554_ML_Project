def replace(path,
            pattern,
            repl,
            count=0,
            flags=0,
            bufsize=1,
            append_if_not_found=False,
            prepend_if_not_found=False,
            not_found_content=None,
            backup='.bak',
            dry_run=False,
            search_only=False,
            show_changes=True,
        ):
    '''
    .. versionadded:: 0.17.0

    Replace occurrences of a pattern in a file

    This is a pure Python implementation that wraps Python's :py:func:`~re.sub`.

    path
        Filesystem path to the file to be edited
    pattern
        Python's regular expression search
        https://docs.python.org/2/library/re.html
    repl
        The replacement text
    count
        Maximum number of pattern occurrences to be replaced.  Defaults to 0.
        If count is a positive integer n, only n occurrences will be replaced,
        otherwise all occurrences will be replaced.
    flags (list or int)
        A list of flags defined in the :ref:`re module documentation
        <contents-of-module-re>`. Each list item should be a string that will
        correlate to the human-friendly flag name. E.g., ``['IGNORECASE',
        'MULTILINE']``. Note: multiline searches must specify ``file`` as the
        ``bufsize`` argument below.
    bufsize (int or str)
        How much of the file to buffer into memory at once. The
        default value ``1`` processes one line at a time. The special value
        ``file`` may be specified which will read the entire file into memory
        before processing. Note: multiline searches must specify ``file``
        buffering.
    append_if_not_found
        .. versionadded:: 2014.7.0

        If pattern is not found and set to ``True``
        then, the content will be appended to the file.
        Default is ``False``
    prepend_if_not_found
        .. versionadded:: 2014.7.0

        If pattern is not found and set to ``True``
        then, the content will be appended to the file.
        Default is ``False``
    not_found_content
        .. versionadded:: 2014.7.0

        Content to use for append/prepend if not found. If
        None (default), uses ``repl``. Useful when ``repl`` uses references to group in
        pattern.
    backup
        The file extension to use for a backup of the file before
        editing. Set to ``False`` to skip making a backup. Default
        is ``.bak``
    dry_run
        Don't make any edits to the file, Default is ``False``
    search_only
        Just search for the pattern; ignore the replacement;
        stop on the first match. Default is ``False``
    show_changes
        Output a unified diff of the old file and the new
        file. If ``False`` return a boolean if any changes were made.
        Default is ``True``

        .. note::

            Using this option will store two copies of the file in-memory
            (the original version and the edited version) in order to generate the
            diff.

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
        raise SaltInvocationError('File not found: {0}'.format(path))

    if not salt.utils.istextfile(path):
        raise SaltInvocationError(
            'Cannot perform string replacements on a binary file: {0}'
            .format(path)
        )

    if search_only and (append_if_not_found or prepend_if_not_found):
        raise SaltInvocationError('Choose between search_only and append/prepend_if_not_found')

    if append_if_not_found and prepend_if_not_found:
        raise SaltInvocationError('Choose between append or prepend_if_not_found')

    flags_num = _get_flags(flags)
    cpattern = re.compile(str(pattern), flags_num)
    if bufsize == 'file':
        bufsize = os.path.getsize(path)

    # Search the file; track if any changes have been made for the return val
    has_changes = False
    orig_file = []  # used if show_changes
    new_file = []  # used if show_changes
    if not salt.utils.is_windows():
        pre_user = get_user(path)
        pre_group = get_group(path)
        pre_mode = __salt__['config.manage_mode'](get_mode(path))

    # Avoid TypeErrors by forcing repl to be a string
    repl = str(repl)

    found = False
    temp_file = None
    content = str(not_found_content) if not_found_content and \
                                       (prepend_if_not_found or
                                        append_if_not_found) \
                                     else repl

    # First check the whole file, determine whether to make the replacement
    # Searching first avoids modifying the time stamp if there are no changes
    try:
        # Use a read-only handle to open the file
        with salt.utils.fopen(path,
                              mode='rb',
                              buffering=bufsize) as r_file:
            for line in r_file:
                if search_only:
                    # Just search; bail as early as a match is found
                    if re.search(cpattern, line):
                        return True  # `with` block handles file closure
                else:
                    result, nrepl = re.subn(cpattern, repl, line, count)

                    # found anything? (even if no change)
                    if nrepl > 0:
                        found = True

                    if prepend_if_not_found or append_if_not_found:
                        # Search for content, so we don't continue pre/appending
                        # the content if it's been pre/appended in a previous run.
                        if re.search('^{0}$'.format(re.escape(content)), line):
                            # Content was found, so set found.
                            found = True

                    # Identity check each potential change until one change is made
                    if has_changes is False and result != line:
                        has_changes = True

                    # Keep track of show_changes here, in case the file isn't
                    # modified
                    if show_changes or append_if_not_found or \
                       prepend_if_not_found:
                        orig_file.append(line)
                        new_file.append(result)

    except (OSError, IOError) as exc:
        raise CommandExecutionError(
            "Unable to open file '{0}'. "
            "Exception: {1}".format(path, exc)
            )

    # Just search. We've searched the whole file now; if we didn't return True
    # already, then the pattern isn't present, so return False.
    if search_only:
        return False

    if has_changes and not dry_run:
        # Write the replacement text in this block.
        try:
            # Create a copy to read from and to use as a backup later
            temp_file = _mkstemp_copy(path=path, preserve_inode=False)
        except (OSError, IOError) as exc:
            raise CommandExecutionError("Exception: {0}".format(exc))

        try:
            # Open the file in write mode
            with salt.utils.fopen(path,
                        mode='wb',
                        buffering=bufsize) as w_file:
                try:
                    # Open the temp file in read mode
                    with salt.utils.fopen(temp_file,
                                          mode='rb',
                                          buffering=bufsize) as r_file:
                        for line in r_file:
                            result, nrepl = re.subn(cpattern, repl,
                                                    line, count)
                            try:
                                w_file.write(result)
                            except (OSError, IOError) as exc:
                                raise CommandExecutionError(
                                    "Unable to write file '{0}'. Contents may "
                                    "be truncated. Temporary file contains copy "
                                    "at '{1}'. "
                                    "Exception: {2}".format(path, temp_file, exc)
                                    )
                except (OSError, IOError) as exc:
                    raise CommandExecutionError("Exception: {0}".format(exc))
        except (OSError, IOError) as exc:
            raise CommandExecutionError("Exception: {0}".format(exc))

    if not found and (append_if_not_found or prepend_if_not_found):
        if not_found_content is None:
            not_found_content = repl
        if prepend_if_not_found:
            new_file.insert(0, not_found_content + '\n')
        else:
            # append_if_not_found
            # Make sure we have a newline at the end of the file
            if 0 != len(new_file):
                if not new_file[-1].endswith('\n'):
                    new_file[-1] += '\n'
            new_file.append(not_found_content + '\n')
        has_changes = True
        if not dry_run:
            try:
                # Create a copy to read from and for later use as a backup
                temp_file = _mkstemp_copy(path=path, preserve_inode=False)
            except (OSError, IOError) as exc:
                raise CommandExecutionError("Exception: {0}".format(exc))
            # write new content in the file while avoiding partial reads
            try:
                f = salt.utils.atomicfile.atomic_open(path, 'wb')
                for line in new_file:
                    f.write(line)
            finally:
                f.close()

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
        return ''.join(difflib.unified_diff(orig_file, new_file))

    return has_changes