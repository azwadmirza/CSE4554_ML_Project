def line(path, content=None, match=None, mode=None, location=None,
         before=None, after=None, show_changes=True, backup=False,
         quiet=False, indent=True):
    '''
    .. versionadded:: 2015.8.0

    Edit a line in the configuration file. The ``path`` and ``content``
    arguments are required, as well as passing in one of the ``mode``
    options.

    path
        Filesystem path to the file to be edited.

    content
        Content of the line. Allowed to be empty if mode=delete.

    match
        Match the target line for an action by
        a fragment of a string or regular expression.

        If neither ``before`` nor ``after`` are provided, and ``match``
        is also ``None``, match becomes the ``content`` value.

    mode
        Defines how to edit a line. One of the following options is
        required:

        - ensure
            If line does not exist, it will be added. This is based on the
            ``content`` argument.
        - replace
            If line already exists, it will be replaced.
        - delete
            Delete the line, once found.
        - insert
            Insert a line.

        .. note::

            If ``mode=insert`` is used, at least one of the following
            options must also be defined: ``location``, ``before``, or
            ``after``. If ``location`` is used, it takes precedence
            over the other two options.

    location
        Defines where to place content in the line. Note this option is only
        used when ``mode=insert`` is specified. If a location is passed in, it
        takes precedence over both the ``before`` and ``after`` kwargs. Valid
        locations are:

        - start
            Place the content at the beginning of the file.
        - end
            Place the content at the end of the file.

    before
        Regular expression or an exact case-sensitive fragment of the string.
        This option is only used when either the ``ensure`` or ``insert`` mode
        is defined.

    after
        Regular expression or an exact case-sensitive fragment of the string.
        This option is only used when either the ``ensure`` or ``insert`` mode
        is defined.

    show_changes
        Output a unified diff of the old file and the new file.
        If ``False`` return a boolean if any changes were made.
        Default is ``True``

        .. note::
            Using this option will store two copies of the file in-memory
            (the original version and the edited version) in order to generate the diff.

    backup
        Create a backup of the original file with the extension:
        "Year-Month-Day-Hour-Minutes-Seconds".

    quiet
        Do not raise any exceptions. E.g. ignore the fact that the file that is
        tried to be edited does not exist and nothing really happened.

    indent
        Keep indentation with the previous line. This option is not considered when
        the ``delete`` mode is specified.

    CLI Example:

    .. code-block:: bash

        salt '*' file.line /etc/nsswitch.conf "networks:\tfiles dns" after="hosts:.*?" mode='ensure'

    .. note::

        If an equal sign (``=``) appears in an argument to a Salt command, it is
        interpreted as a keyword argument in the format of ``key=val``. That
        processing can be bypassed in order to pass an equal sign through to the
        remote shell command by manually specifying the kwarg:

        .. code-block:: bash

            salt '*' file.line /path/to/file content="CREATEMAIL_SPOOL=no" match="CREATE_MAIL_SPOOL=yes" mode="replace"
    '''
    path = os.path.realpath(os.path.expanduser(path))
    if not os.path.isfile(path):
        if not quiet:
            raise CommandExecutionError('File "{0}" does not exists or is not a file.'.format(path))
        return False  # No changes had happened

    mode = mode and mode.lower() or mode
    if mode not in ['insert', 'ensure', 'delete', 'replace']:
        if mode is None:
            raise CommandExecutionError('Mode was not defined. How to process the file?')
        else:
            raise CommandExecutionError('Unknown mode: "{0}"'.format(mode))

    # We've set the content to be empty in the function params but we want to make sure
    # it gets passed when needed. Feature #37092
    empty_content_modes = ['delete']
    if mode not in empty_content_modes and content is None:
        raise CommandExecutionError('Content can only be empty if mode is "{0}"'.format(', '.join(empty_content_modes)))
    del empty_content_modes

    # Before/after has privilege. If nothing defined, match is used by content.
    if before is None and after is None and not match:
        match = content

    with salt.utils.files.fopen(path, mode='r') as fp_:
        body = salt.utils.stringutils.to_unicode(fp_.read())
    body_before = hashlib.sha256(salt.utils.stringutils.to_bytes(body)).hexdigest()
    after = _regex_to_static(body, after)
    before = _regex_to_static(body, before)
    match = _regex_to_static(body, match)

    if os.stat(path).st_size == 0 and mode in ('delete', 'replace'):
        log.warning('Cannot find text to {0}. File \'{1}\' is empty.'.format(mode, path))
        body = ''
    elif mode == 'delete':
        body = os.linesep.join([line for line in body.split(os.linesep) if line.find(match) < 0])
    elif mode == 'replace':
        body = os.linesep.join([(_get_line_indent(file_line, content, indent)
                                if (file_line.find(match) > -1 and not file_line == content) else file_line)
                                for file_line in body.split(os.linesep)])
    elif mode == 'insert':
        if not location and not before and not after:
            raise CommandExecutionError('On insert must be defined either "location" or "before/after" conditions.')

        if not location:
            if before and after:
                _assert_occurrence(body, before, 'before')
                _assert_occurrence(body, after, 'after')
                out = []
                lines = body.split(os.linesep)
                in_range = False
                for line in lines:
                    if line.find(after) > -1:
                        in_range = True
                    elif line.find(before) > -1 and in_range:
                        out.append(_get_line_indent(line, content, indent))
                    out.append(line)
                body = os.linesep.join(out)

            if before and not after:
                _assert_occurrence(body, before, 'before')
                out = []
                lines = body.split(os.linesep)
                for idx in range(len(lines)):
                    _line = lines[idx]
                    if _line.find(before) > -1:
                        cnd = _get_line_indent(_line, content, indent)
                        if not idx or (idx and _starts_till(lines[idx - 1], cnd) < 0):  # Job for replace instead
                            out.append(cnd)
                    out.append(_line)
                body = os.linesep.join(out)

            elif after and not before:
                _assert_occurrence(body, after, 'after')
                out = []
                lines = body.split(os.linesep)
                for idx, _line in enumerate(lines):
                    out.append(_line)
                    cnd = _get_line_indent(_line, content, indent)
                    # No duplicates or append, if "after" is the last line
                    if (_line.find(after) > -1 and
                            (lines[((idx + 1) < len(lines)) and idx + 1 or idx].strip() != cnd or
                             idx + 1 == len(lines))):
                        out.append(cnd)
                body = os.linesep.join(out)

        else:
            if location == 'start':
                body = os.linesep.join((content, body))
            elif location == 'end':
                body = os.linesep.join((body, _get_line_indent(body[-1], content, indent) if body else content))

    elif mode == 'ensure':
        after = after and after.strip()
        before = before and before.strip()

        if before and after:
            _assert_occurrence(body, before, 'before')
            _assert_occurrence(body, after, 'after')

            is_there = bool(body.count(content))
            if not is_there:
                out = []
                body = body.split(os.linesep)
                for idx, line in enumerate(body):
                    out.append(line)
                    if line.find(content) > -1:
                        is_there = True
                    if not is_there:
                        if idx < (len(body) - 1) and line.find(after) > -1 and body[idx + 1].find(before) > -1:
                            out.append(content)
                        elif line.find(after) > -1:
                            raise CommandExecutionError('Found more than one line between '
                                                        'boundaries "before" and "after".')
                body = os.linesep.join(out)

        elif before and not after:
            _assert_occurrence(body, before, 'before')
            body = body.split(os.linesep)
            out = []
            for idx in range(len(body)):
                if body[idx].find(before) > -1:
                    prev = (idx > 0 and idx or 1) - 1
                    out.append(_get_line_indent(body[idx], content, indent))
                    if _starts_till(out[prev], content) > -1:
                        del out[prev]
                out.append(body[idx])
            body = os.linesep.join(out)

        elif not before and after:
            _assert_occurrence(body, after, 'after')
            body = body.split(os.linesep)
            skip = None
            out = []
            for idx in range(len(body)):
                if skip != body[idx]:
                    out.append(body[idx])

                if body[idx].find(after) > -1:
                    next_line = idx + 1 < len(body) and body[idx + 1] or None
                    if next_line is not None and _starts_till(next_line, content) > -1:
                        skip = next_line
                    out.append(_get_line_indent(body[idx], content, indent))
            body = os.linesep.join(out)

        else:
            raise CommandExecutionError("Wrong conditions? "
                                        "Unable to ensure line without knowing "
                                        "where to put it before and/or after.")

    changed = body_before != hashlib.sha256(salt.utils.stringutils.to_bytes(body)).hexdigest()

    if backup and changed and __opts__['test'] is False:
        try:
            temp_file = _mkstemp_copy(path=path, preserve_inode=True)
            shutil.move(temp_file, '{0}.{1}'.format(path, time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime())))
        except (OSError, IOError) as exc:
            raise CommandExecutionError("Unable to create the backup file of {0}. Exception: {1}".format(path, exc))

    changes_diff = None

    if changed:
        if show_changes:
            with salt.utils.files.fopen(path, 'r') as fp_:
                path_content = [salt.utils.stringutils.to_unicode(x)
                                for x in fp_.read().splitlines(True)]
            changes_diff = ''.join(difflib.unified_diff(
                path_content,
                [salt.utils.stringutils.to_unicode(x)
                 for x in body.splitlines(True)]
            ))
        if __opts__['test'] is False:
            fh_ = None
            try:
                # Make sure we match the file mode from salt.utils.files.fopen
                if six.PY2 and salt.utils.platform.is_windows():
                    mode = 'wb'
                    body = salt.utils.stringutils.to_bytes(body)
                else:
                    mode = 'w'
                    body = salt.utils.stringutils.to_str(body)
                fh_ = salt.utils.atomicfile.atomic_open(path, mode)
                fh_.write(body)
            finally:
                if fh_:
                    fh_.close()

    return show_changes and changes_diff or changed