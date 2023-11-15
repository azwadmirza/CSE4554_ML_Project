def line(path, content, match=None, mode=None, location=None,
         before=None, after=None, show_changes=True, backup=False,
         quiet=False, indent=True):
    '''
    .. versionadded:: 2015.8.0

    Edit a line in the configuration file.

    :param path:
        Filesystem path to the file to be edited.

    :param content:
        Content of the line.

    :param match:
        Match the target line for an action by
        a fragment of a string or regular expression.

    :param mode:
        :Ensure:
            If line does not exist, it will be added.

        :Replace:
            If line already exist, it will be replaced.

        :Delete:
            Delete the line, once found.

        :Insert:
            Insert a line.

    :param location:
        :start:
            Place the content at the beginning of the file.

        :end:
            Place the content at the end of the file.

    :param before:
        Regular expression or an exact case-sensitive fragment of the string.

    :param after:
        Regular expression or an exact case-sensitive fragment of the string.

    :param show_changes:
        Output a unified diff of the old file and the new file.
        If ``False`` return a boolean if any changes were made.
        Default is ``True``

        .. note::
            Using this option will store two copies of the file in-memory
            (the original version and the edited version) in order to generate the diff.

    :param backup:
        Create a backup of the original file with the extension:
        "Year-Month-Day-Hour-Minutes-Seconds".

    :param quiet:
        Do not raise any exceptions. E.g. ignore the fact that the file that is
        tried to be edited does not exist and nothing really happened.

    :param indent:
        Keep indentation with the previous line.

    If an equal sign (``=``) appears in an argument to a Salt command, it is
    interpreted as a keyword argument in the format of ``key=val``. That
    processing can be bypassed in order to pass an equal sign through to the
    remote shell command by manually specifying the kwarg:

    .. code-block:: bash

        salt '*' file.line /path/to/file content="CREATEMAIL_SPOOL=no" match="CREATE_MAIL_SPOOL=yes" mode="replace"

    CLI Examples:

    .. code-block:: bash

        salt '*' file.line /etc/nsswitch.conf "networks:\tfiles dns" after="hosts:.*?" mode='ensure'
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

    # Before/after has privilege. If nothing defined, match is used by content.
    if before is None and after is None and not match:
        match = content

    with salt.utils.fopen(path, mode='r') as fp_:
        body = fp_.read()
    body_before = hashlib.sha256(salt.utils.to_bytes(body)).hexdigest()
    after = _regex_to_static(body, after)
    before = _regex_to_static(body, before)
    match = _regex_to_static(body, match)

    if mode == 'delete':
        body = os.linesep.join([line for line in body.split(os.linesep) if line.find(match) < 0])

    elif mode == 'replace':
        body = os.linesep.join([(_get_line_indent(line, content, indent)
                                if (line.find(match) > -1 and not line == content) else line)
                                for line in body.split(os.linesep)])
    elif mode == 'insert':
        if not location and not before and not after:
            raise CommandExecutionError('On insert must be defined either "location" or "before/after" conditions.')

        if not location:
            if before and after:
                _assert_occurrence(body, before, 'before')
                _assert_occurrence(body, after, 'after')
                out = []
                lines = body.split(os.linesep)
                for idx in range(len(lines)):
                    _line = lines[idx]
                    if _line.find(before) > -1 and idx <= len(lines) and lines[idx - 1].find(after) > -1:
                        out.append(_get_line_indent(_line, content, indent))
                        out.append(_line)
                    else:
                        out.append(_line)
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
                for idx in range(len(lines)):
                    _line = lines[idx]
                    out.append(_line)
                    cnd = _get_line_indent(_line, content, indent)
                    if _line.find(after) > -1:
                        # No dupes or append, if "after" is the last line
                        if (idx < len(lines) and _starts_till(lines[idx + 1], cnd) < 0) or idx + 1 == len(lines):
                            out.append(cnd)
                body = os.linesep.join(out)

        else:
            if location == 'start':
                body = ''.join([content, body])
            elif location == 'end':
                body = ''.join([body, _get_line_indent(body[-1], content, indent) if body else content])

    elif mode == 'ensure':
        after = after and after.strip()
        before = before and before.strip()
        content = content and content.strip()

        if before and after:
            _assert_occurrence(body, before, 'before')
            _assert_occurrence(body, after, 'after')

            a_idx = b_idx = -1
            idx = 0
            body = body.split(os.linesep)
            for _line in body:
                idx += 1
                if _line.find(before) > -1 and b_idx < 0:
                    b_idx = idx
                if _line.find(after) > -1 and a_idx < 0:
                    a_idx = idx

            # Add
            if not b_idx - a_idx - 1:
                body = body[:a_idx] + [content] + body[b_idx - 1:]
            elif b_idx - a_idx - 1 == 1:
                if _starts_till(body[a_idx:b_idx - 1][0], content) > -1:
                    body[a_idx] = _get_line_indent(body[a_idx - 1], content, indent)
            else:
                raise CommandExecutionError('Found more than one line between boundaries "before" and "after".')
            body = os.linesep.join(body)

        elif before and not after:
            _assert_occurrence(body, before, 'before')
            body = body.split(os.linesep)
            out = []
            for idx in range(len(body)):
                if body[idx].find(before) > -1:
                    prev = (idx > 0 and idx or 1) - 1
                    out.append(_get_line_indent(body[prev], content, indent))
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

    changed = body_before != hashlib.sha256(salt.utils.to_bytes(body)).hexdigest()

    if backup and changed and __opts__['test'] is False:
        try:
            temp_file = _mkstemp_copy(path=path, preserve_inode=True)
            shutil.move(temp_file, '{0}.{1}'.format(path, time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime())))
        except (OSError, IOError) as exc:
            raise CommandExecutionError("Unable to create the backup file of {0}. Exception: {1}".format(path, exc))

    changes_diff = None

    if changed:
        if show_changes:
            with salt.utils.fopen(path, 'r') as fp_:
                path_content = fp_.read().splitlines()
            changes_diff = ''.join(difflib.unified_diff(path_content, body.splitlines()))
        if __opts__['test'] is False:
            fh_ = None
            try:
                fh_ = salt.utils.atomicfile.atomic_open(path, 'w')
                fh_.write(body)
            finally:
                if fh_:
                    fh_.close()

    return show_changes and changes_diff or changed