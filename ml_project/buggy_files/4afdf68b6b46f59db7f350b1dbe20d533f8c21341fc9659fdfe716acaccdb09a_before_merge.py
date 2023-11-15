def replace(path,
        pattern,
        repl,
        count=0,
        flags=0,
        bufsize=1,
        backup='.bak',
        dry_run=False,
        search_only=False,
        show_changes=True,
        ):
    '''
    Replace occurances of a pattern in a file

    .. versionadded:: 0.17

    This is a pure Python implementation that wraps Python's :py:func:`~re.sub`.

    :param path: Filesystem path to the file to be edited
    :param pattern: The PCRE search
    :param repl: The replacement text
    :param count: Maximum number of pattern occurrences to be replaced
    :param flags: A list of flags defined in :ref:`contents-of-module-re`. Each
        list item should be a string that will correlate to the human-friendly
        flag name. E.g., ``['IGNORECASE', 'MULTILINE']``. Note: multiline
        searches must specify ``file`` as the ``bufsize`` argument below.
    :type flags: list or int
    :param bufsize: How much of the file to buffer into memory at once. The
        default value ``1`` processes one line at a time. The special value
        ``file`` may be specified which will read the entire file into memory
        before processing. Note: multiline searches must specify ``file``
        buffering.
    :type bufsize: int or str
    :param backup: The file extension to use for a backup of the file before
        editing. Set to ``False`` to skip making a backup.
    :param dry_run: Don't make any edits to the file
    :param search_only: Just search for the pattern; ignore the replacement;
        stop on the first match
    :param show_changes: Output a unified diff of the old file and the new
        file. If ``False`` return a boolean if any changes were made.
        Note: using this option will store two copies of the file in-memory
        (the original version and the edited version) in order to generate the
        diff.

    :rtype: bool or str

    CLI Example:

    .. code-block:: bash

        salt '*' file.replace /etc/httpd/httpd.conf 'LogLevel warn' 'LogLevel info'
        salt '*' file.replace /some/file 'before' 'after' flags='[MULTILINE, IGNORECASE]'
    '''
    if not os.path.exists(path):
        raise SaltInvocationError("File not found: %s", path)

    if not salt.utils.istextfile(path):
        raise SaltInvocationError(
            "Cannot perform string replacements on a binary file: %s", path)

    flags_num = _get_flags(flags)
    cpattern = re.compile(pattern, flags_num)
    if bufsize == 'file':
        bufsize = os.path.getsize(path)

    # Search the file; track if any changes have been made for the return val
    has_changes = False
    orig_file = []  # used if show_changes
    new_file = []  # used if show_changes
    for line in fileinput.input(path,
            inplace=not dry_run, backup=False if dry_run else backup,
            bufsize=bufsize, mode='rb'):

        if search_only:
            # Just search; bail as early as a match is found
            result = re.search(cpattern, line)

            if result:
                return True
        else:
            result = re.sub(cpattern, repl, line, count)

            # Identity check each potential change until one change is made
            if has_changes is False and not result is line:
                has_changes = True

            if show_changes:
                orig_file.append(line)
                new_file.append(result)

            if not dry_run:
                print(result, end='', file=sys.stdout)

    if show_changes:
        return ''.join(difflib.unified_diff(orig_file, new_file))

    return has_changes