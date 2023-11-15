def blockreplace(
        name,
        marker_start='#-- start managed zone --',
        marker_end='#-- end managed zone --',
        content='',
        append_if_not_found=False,
        prepend_if_not_found=False,
        backup='.bak',
        show_changes=True):
    '''
    Maintain an edit in a file in a zone delimited by two line markers

    .. versionadded:: 2014.1.0

    A block of content delimited by comments can help you manage several lines
    entries without worrying about old entries removal. This can help you
    maintaining an un-managed file containing manual edits.
    Note: this function will store two copies of the file in-memory
    (the original version and the edited version) in order to detect changes
    and only edit the targeted file if necessary.

    :param name: Filesystem path to the file to be edited
    :param marker_start: The line content identifying a line as the start of
        the content block. Note that the whole line containing this marker will
        be considered, so whitespace or extra content before or after the
        marker is included in final output
    :param marker_end: The line content identifying a line as the end of
        the content block. Note that the whole line containing this marker will
        be considered, so whitespace or extra content before or after the
        marker is included in final output.
        Note: you can use file.accumulated and target this state. All
        accumulated data dictionaries content will be added as new lines in the
        content.
    :param content: The content to be used between the two lines identified by
        marker_start and marker_stop.
    :param append_if_not_found: False by default, if markers are not found and
        set to True then the markers and content will be appended to the file
    :param prepend_if_not_found: False by default, if markers are not found and
        set to True then the markers and content will be prepended to the file
    :param backup: The file extension to use for a backup of the file if any
        edit is made. Set to ``False`` to skip making a backup.
    :param dry_run: Don't make any edits to the file
    :param show_changes: Output a unified diff of the old file and the new
        file. If ``False`` return a boolean if any changes were made.

    :rtype: bool or str

    Example of usage with an accumulator and with a variable:

    .. code-block:: yaml

        {% set myvar = 42 %}
        hosts-config-block-{{ myvar }}:
          file.blockreplace:
            - name: /etc/hosts
            - marker_start: "# START managed zone {{ myvar }} -DO-NOT-EDIT-"
            - marker_end: "# END managed zone {{ myvar }} --"
            - content: 'First line of content'
            - append_if_not_found: True
            - backup: '.bak'
            - show_changes: True

        hosts-config-block-{{ myvar }}-accumulated1:
          file.accumulated:
            - filename: /etc/hosts
            - name: my-accumulator-{{ myvar }}
            - text: "text 2"
            - require_in:
              - file: hosts-config-block-{{ myvar }}

        hosts-config-block-{{ myvar }}-accumulated2:
          file.accumulated:
            - filename: /etc/hosts
            - name: my-accumulator-{{ myvar }}
            - text: |
                 text 3
                 text 4
            - require_in:
              - file: hosts-config-block-{{ myvar }}

    will generate and maintain a block of content in ``/etc/hosts``:

    .. code-block:: text

        # START managed zone 42 -DO-NOT-EDIT-
        First line of content
        text 2
        text 3
        text 4
        # END managed zone 42 --
    '''
    ret = {'name': name, 'changes': {}, 'result': False, 'comment': ''}

    check_res, check_msg = _check_file(name)
    if not check_res:
        return _error(ret, check_msg)

    if name in _ACCUMULATORS:
        accumulator = _ACCUMULATORS[name]
        # if we have multiple accumulators for a file, only apply the one
        # required at a time
        deps = _ACCUMULATORS_DEPS.get(name, [])
        filtered = [a for a in deps if
                    __low__['__id__'] in deps[a] and a in accumulator]
        if not filtered:
            filtered = [a for a in accumulator]
        for acc in filtered:
            acc_content = accumulator[acc]
            for line in acc_content:
                if content == '':
                    content = line
                else:
                    content += "\n" + line

    changes = __salt__['file.blockreplace'](
        name,
        marker_start,
        marker_end,
        content=content,
        append_if_not_found=append_if_not_found,
        prepend_if_not_found=prepend_if_not_found,
        backup=backup,
        dry_run=__opts__['test'],
        show_changes=show_changes
    )

    if changes:
        ret['changes'] = {'diff': changes}
        if __opts__['test']:
            ret['result'] = None
            ret['comment'] = 'Changes would be made'
        else:
            ret['result'] = True
            ret['comment'] = 'Changes were made'
    else:
        ret['result'] = True
        ret['comment'] = 'No changes needed to be made'

    return ret