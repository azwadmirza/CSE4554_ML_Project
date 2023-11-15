def _format_host(host, data):
    colors = salt.utils.get_colors(__opts__.get('color'))
    tabular = __opts__.get('state_tabular', False)
    rcounts = {}
    hcolor = colors['GREEN']
    hstrs = []
    nchanges = 0
    strip_colors = __opts__.get('strip_colors', True)
    if isinstance(data, list):
        # Errors have been detected, list them in RED!
        hcolor = colors['RED_BOLD']
        hstrs.append((u'    {0}Data failed to compile:{1[ENDC]}'
                      .format(hcolor, colors)))
        for err in data:
            if strip_colors:
                err = salt.output.strip_esc_sequence(err)
            hstrs.append((u'{0}----------\n    {1}{2[ENDC]}'
                          .format(hcolor, err, colors)))
    if isinstance(data, dict):
        # Strip out the result: True, without changes returns if
        # state_verbose is False
        if not __opts__.get('state_verbose', False):
            data = _strip_clean(data)
        # Verify that the needed data is present
        for tname, info in data.items():
            if '__run_num__' not in info:
                err = (u'The State execution failed to record the order '
                       'in which all states were executed. The state '
                       'return missing data is:')
                hstrs.insert(0, pprint.pformat(info))
                hstrs.insert(0, err)
        # Everything rendered as it should display the output
        for tname in sorted(
                data,
                key=lambda k: data[k].get('__run_num__', 0)):
            ret = data[tname]
            # Increment result counts
            rcounts.setdefault(ret['result'], 0)
            rcounts[ret['result']] += 1

            tcolor = colors['GREEN']
            schanged, ctext = _format_changes(ret['changes'])
            nchanges += 1 if schanged else 0

            # Skip this state if it was successfull & diff output was requested
            if __opts__.get('state_output_diff', False) and \
               ret['result'] and not schanged:
                continue

            if schanged:
                tcolor = colors['CYAN']
            if ret['result'] is False:
                hcolor = colors['RED']
                tcolor = colors['RED']
            if ret['result'] is None:
                hcolor = colors['YELLOW']
                tcolor = colors['YELLOW']
            comps = tname.split('_|-')
            if __opts__.get('state_output', 'full').lower() == 'filter':
                # By default, full data is shown for all types. However, return
                # data may be excluded by setting state_output_exclude to a
                # comma-separated list of True, False or None, or including the
                # same list with the exclude option on the command line. For
                # now, this option must include a comma. For example:
                #     exclude=True,
                # The same functionality is also available for making return
                # data terse, instead of excluding it.
                cliargs = __opts__.get('arg', [])
                clikwargs = {}
                for item in cliargs:
                    if isinstance(item, dict) and '__kwarg__' in item:
                        clikwargs = item.copy()

                exclude = clikwargs.get(
                    'exclude', __opts__.get('state_output_exclude', [])
                )
                if isinstance(exclude, string_types):
                    exclude = str(exclude).split(',')

                terse = clikwargs.get(
                    'terse', __opts__.get('state_output_terse', [])
                )
                if isinstance(terse, string_types):
                    terse = str(terse).split(',')

                if str(ret['result']) in terse:
                    msg = _format_terse(tcolor, comps, ret, colors, tabular)
                    hstrs.append(msg)
                    continue
                if str(ret['result']) in exclude:
                    continue
            elif __opts__.get('state_output', 'full').lower() == 'terse':
                # Print this chunk in a terse way and continue in the
                # loop
                msg = _format_terse(tcolor, comps, ret, colors, tabular)
                hstrs.append(msg)
                continue
            elif __opts__.get('state_output', 'full').lower() == 'mixed':
                # Print terse unless it failed
                if ret['result'] is not False:
                    msg = _format_terse(tcolor, comps, ret, colors, tabular)
                    hstrs.append(msg)
                    continue
            elif __opts__.get('state_output', 'full').lower() == 'changes':
                # Print terse if no error and no changes, otherwise, be
                # verbose
                if ret['result'] and not schanged:
                    msg = _format_terse(tcolor, comps, ret, colors, tabular)
                    hstrs.append(msg)
                    continue
            state_lines = [
                u'{tcolor}----------{colors[ENDC]}',
                u'    {tcolor}      ID: {comps[1]}{colors[ENDC]}',
                u'    {tcolor}Function: {comps[0]}.{comps[3]}{colors[ENDC]}',
                u'    {tcolor}  Result: {ret[result]!s}{colors[ENDC]}',
                u'    {tcolor} Comment: {comment}{colors[ENDC]}',
                u'    {tcolor} Started: {ret[start_time]!s}{colors[ENDC]}',
                u'    {tcolor}Duration: {ret[duration]!s}{colors[ENDC]}'
            ]
            # This isn't the prettiest way of doing this, but it's readable.
            if comps[1] != comps[2]:
                state_lines.insert(
                    3, u'    {tcolor}    Name: {comps[2]}{colors[ENDC]}')
            try:
                stripped_comment = ret['comment'].strip()
            except AttributeError:  # Assume comment is a list
                try:
                    comment = ret['comment'].join(' ').replace(
                        u'\n',
                        u'\n' + u' ' * 13)
                except AttributeError:
                    # Comment isn't a list either, just convert to string
                    comment = str(ret['comment'])
                    comment = comment.strip().replace(
                        u'\n',
                        u'\n' + u' ' * 14)
            else:
                try:
                    comment = stripped_comment.replace(
                        u'\n',
                        u'\n' + u' ' * 14)
                except UnicodeDecodeError:
                    comment = stripped_comment.replace(
                        '\n',
                        '\n' + ' ' * 14)
                    comment = comment.decode('UTF-8')
            for detail in ['start_time', 'duration']:
                ret.setdefault(detail, u'')
            if ret['duration'] != '':
                ret['duration'] = u'{0} ms'.format(ret['duration'])
            svars = {
                'tcolor': tcolor,
                'comps': comps,
                'ret': ret,
                'comment': comment,
                # This nukes any trailing \n and indents the others.
                'colors': colors
            }
            hstrs.extend([sline.format(**svars) for sline in state_lines])
            changes = u'     Changes:   ' + ctext
            hstrs.append((u'{0}{1}{2[ENDC]}'
                          .format(tcolor, changes, colors)))

        # Append result counts to end of output
        colorfmt = u'{0}{1}{2[ENDC]}'
        rlabel = {True: u'Succeeded', False: u'Failed', None: u'Not Run'}
        count_max_len = max([len(str(x)) for x in rcounts.values()] or [0])
        label_max_len = max([len(x) for x in rlabel.values()] or [0])
        line_max_len = label_max_len + count_max_len + 2  # +2 for ': '
        hstrs.append(
            colorfmt.format(
                colors['CYAN'],
                u'\nSummary\n{0}'.format('-' * line_max_len),
                colors
            )
        )

        def _counts(label, count):
            return u'{0}: {1:>{2}}'.format(
                label,
                count,
                line_max_len - (len(label) + 2)
            )

        # Successful states
        changestats = []
        if None in rcounts and rcounts.get(None, 0) > 0:
            # test=True states
            changestats.append(
                colorfmt.format(
                    colors['YELLOW'],
                    u'unchanged={0}'.format(rcounts.get(None, 0)),
                    colors
                )
            )
        if nchanges > 0:
            changestats.append(
                colorfmt.format(
                    colors['GREEN'],
                    u'changed={0}'.format(nchanges),
                    colors
                )
            )
        if changestats:
            changestats = u' ({0})'.format(', '.join(changestats))
        else:
            changestats = u''
        hstrs.append(
            colorfmt.format(
                colors['GREEN'],
                _counts(
                    rlabel[True],
                    rcounts.get(True, 0) + rcounts.get(None, 0)
                ),
                colors
            ) + changestats
        )

        # Failed states
        num_failed = rcounts.get(False, 0)
        hstrs.append(
            colorfmt.format(
                colors['RED'] if num_failed else colors['CYAN'],
                _counts(rlabel[False], num_failed),
                colors
            )
        )

        totals = u'{0}\nTotal states run: {1:>{2}}'.format('-' * line_max_len,
                                               sum(rcounts.values()),
                                               line_max_len - 7)
        hstrs.append(colorfmt.format(colors['CYAN'], totals, colors))

    if strip_colors:
        host = salt.output.strip_esc_sequence(host)
    hstrs.insert(0, (u'{0}{1}:{2[ENDC]}'.format(hcolor, host, colors)))
    return u'\n'.join(hstrs), nchanges > 0