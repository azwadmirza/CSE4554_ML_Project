def present(module, dest, regexp, line, insertafter, insertbefore, create,
            backup, backrefs, firstmatch):

    diff = {'before': '',
            'after': '',
            'before_header': '%s (content)' % dest,
            'after_header': '%s (content)' % dest}

    b_dest = to_bytes(dest, errors='surrogate_or_strict')
    if not os.path.exists(b_dest):
        if not create:
            module.fail_json(rc=257, msg='Destination %s does not exist !' % dest)
        b_destpath = os.path.dirname(b_dest)
        if not os.path.exists(b_destpath) and not module.check_mode:
            try:
                os.makedirs(b_destpath)
            except Exception as e:
                module.fail_json(msg='Error creating %s Error code: %s Error description: %s' % (b_destpath, e[0], e[1]))

        b_lines = []
    else:
        with open(b_dest, 'rb') as f:
            b_lines = f.readlines()

    if module._diff:
        diff['before'] = to_native(b''.join(b_lines))

    if regexp is not None:
        bre_m = re.compile(to_bytes(regexp, errors='surrogate_or_strict'))

    if insertafter not in (None, 'BOF', 'EOF'):
        bre_ins = re.compile(to_bytes(insertafter, errors='surrogate_or_strict'))
    elif insertbefore not in (None, 'BOF'):
        bre_ins = re.compile(to_bytes(insertbefore, errors='surrogate_or_strict'))
    else:
        bre_ins = None

    # index[0] is the line num where regexp has been found
    # index[1] is the line num where insertafter/insertbefore has been found
    index = [-1, -1]
    match = None
    exact_line_match = False
    b_line = to_bytes(line, errors='surrogate_or_strict')

    # The module's doc says
    # "If regular expressions are passed to both regexp and
    # insertafter, insertafter is only honored if no match for regexp is found."
    # Therefore:
    # 1. regexp was found -> ignore insertafter, replace the founded line
    # 2. regexp was not found -> insert the line after 'insertafter' or 'insertbefore' line

    # Given the above:
    # 1. First check that there is no match for regexp:
    if regexp is not None:
        for lineno, b_cur_line in enumerate(b_lines):
            match_found = bre_m.search(b_cur_line)
            if match_found:
                index[0] = lineno
                match = match_found
                if firstmatch:
                    break

    # 2. When no match found on the previous step,
    # parse for searching insertafter/insertbefore:
    if not match:
        for lineno, b_cur_line in enumerate(b_lines):
            if b_line == b_cur_line.rstrip(b'\r\n'):
                index[0] = lineno
                exact_line_match = True

            elif bre_ins is not None and bre_ins.search(b_cur_line):
                if insertafter:
                    # + 1 for the next line
                    index[1] = lineno + 1
                    if firstmatch:
                        break

                if insertbefore:
                    # index[1] for the previous line
                    index[1] = lineno
                    if firstmatch:
                        break

    msg = ''
    changed = False
    b_linesep = to_bytes(os.linesep, errors='surrogate_or_strict')
    # Exact line or Regexp matched a line in the file
    if index[0] != -1:
        if backrefs and match:
            b_new_line = match.expand(b_line)
        else:
            # Don't do backref expansion if not asked.
            b_new_line = b_line

        if not b_new_line.endswith(b_linesep):
            b_new_line += b_linesep

        # If no regexp was given and no line match is found anywhere in the file,
        # insert the line appropriately if using insertbefore or insertafter
        if regexp is None and match is None and not exact_line_match:

            # Insert lines
            if insertafter and insertafter != 'EOF':
                # Ensure there is a line separator after the found string
                # at the end of the file.
                if b_lines and not b_lines[-1][-1:] in (b'\n', b'\r'):
                    b_lines[-1] = b_lines[-1] + b_linesep

                # If the line to insert after is at the end of the file
                # use the appropriate index value.
                if len(b_lines) == index[1]:
                    if b_lines[index[1] - 1].rstrip(b'\r\n') != b_line:
                        b_lines.append(b_line + b_linesep)
                        msg = 'line added'
                        changed = True
                elif b_lines[index[1]].rstrip(b'\r\n') != b_line:
                    b_lines.insert(index[1], b_line + b_linesep)
                    msg = 'line added'
                    changed = True

            elif insertbefore and insertbefore != 'BOF':
                # If the line to insert before is at the beginning of the file
                # use the appropriate index value.
                if index[1] <= 0:
                    if b_lines[index[1]].rstrip(b'\r\n') != b_line:
                        b_lines.insert(index[1], b_line + b_linesep)
                        msg = 'line added'
                        changed = True

                elif b_lines[index[1] - 1].rstrip(b'\r\n') != b_line:
                    b_lines.insert(index[1], b_line + b_linesep)
                    msg = 'line added'
                    changed = True

        elif b_lines[index[0]] != b_new_line:
            b_lines[index[0]] = b_new_line
            msg = 'line replaced'
            changed = True

    elif backrefs:
        # Do absolutely nothing, since it's not safe generating the line
        # without the regexp matching to populate the backrefs.
        pass
    # Add it to the beginning of the file
    elif insertbefore == 'BOF' or insertafter == 'BOF':
        b_lines.insert(0, b_line + b_linesep)
        msg = 'line added'
        changed = True
    # Add it to the end of the file if requested or
    # if insertafter/insertbefore didn't match anything
    # (so default behaviour is to add at the end)
    elif insertafter == 'EOF' or index[1] == -1:

        # If the file is not empty then ensure there's a newline before the added line
        if b_lines and not b_lines[-1][-1:] in (b'\n', b'\r'):
            b_lines.append(b_linesep)

        b_lines.append(b_line + b_linesep)
        msg = 'line added'
        changed = True

    elif insertafter and index[1] != -1:

        # Don't insert the line if it already matches at the index.
        # If the line to insert after is at the end of the file use the appropriate index value.
        if len(b_lines) == index[1]:
            if b_lines[index[1] - 1].rstrip(b'\r\n') != b_line:
                b_lines.append(b_line + b_linesep)
                msg = 'line added'
                changed = True
        elif b_line != b_lines[index[1]].rstrip(b'\n\r'):
            b_lines.insert(index[1], b_line + b_linesep)
            msg = 'line added'
            changed = True

    # insert matched, but not the regexp
    else:
        b_lines.insert(index[1], b_line + b_linesep)
        msg = 'line added'
        changed = True

    if module._diff:
        diff['after'] = to_native(b''.join(b_lines))

    backupdest = ""
    if changed and not module.check_mode:
        if backup and os.path.exists(b_dest):
            backupdest = module.backup_local(dest)
        write_changes(module, b_lines, dest)

    if module.check_mode and not os.path.exists(b_dest):
        module.exit_json(changed=changed, msg=msg, backup=backupdest, diff=diff)

    attr_diff = {}
    msg, changed = check_file_attrs(module, changed, msg, attr_diff)

    attr_diff['before_header'] = '%s (file attributes)' % dest
    attr_diff['after_header'] = '%s (file attributes)' % dest

    difflist = [diff, attr_diff]
    module.exit_json(changed=changed, msg=msg, backup=backupdest, diff=difflist)