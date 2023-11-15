def sed(name,
        before,
        after,
        limit='',
        backup='.bak',
        options='-r -e',
        flags='g',
        negate_match=False):
    '''
    .. deprecated:: 0.17.0
       Use :py:func:`~salt.states.file.replace` instead.

    Maintain a simple edit to a file

    The file will be searched for the ``before`` pattern before making the
    edit.  In general the ``limit`` pattern should be as specific as possible
    and ``before`` and ``after`` should contain the minimal text to be changed.

    before
        A pattern that should exist in the file before the edit.
    after
        A pattern that should exist in the file after the edit.
    limit
        An optional second pattern that can limit the scope of the before
        pattern.
    backup : '.bak'
        The extension for the backed-up version of the file before the edit. If
        no backups is desired, pass in the empty string: ''
    options : ``-r -e``
        Any options to pass to the ``sed`` command. ``-r`` uses extended
        regular expression syntax and ``-e`` denotes that what follows is an
        expression that sed will execute.
    flags : ``g``
        Any flags to append to the sed expression. ``g`` specifies the edit
        should be made globally (and not stop after the first replacement).
    negate_match : False
        Negate the search command (``!``)

        .. versionadded:: 0.17.0

    Usage::

        # Disable the epel repo by default
        /etc/yum.repos.d/epel.repo:
          file.sed:
            - before: 1
            - after: 0
            - limit: ^enabled=

        # Remove ldap from nsswitch
        /etc/nsswitch.conf:
          file.sed:
            - before: 'ldap'
            - after: ''
            - limit: '^passwd:'

    .. versionadded:: 0.9.5
    '''
    ret = {'name': name, 'changes': {}, 'result': False, 'comment': ''}

    check_res, check_msg = _check_file(name)
    if not check_res:
        return _error(ret, check_msg)

    # Mandate that before and after are strings
    before = str(before)
    after = str(after)

    # Look for the pattern before attempting the edit
    if not __salt__['file.sed_contains'](name,
                                         before,
                                         limit=limit,
                                         flags=flags):
        # Pattern not found; don't try to guess why, just tell the user there
        # were no changes made, as the changes should only be made once anyway.
        # This makes it so users can use backreferences without the state
        # coming back as failed all the time.
        ret['comment'] = '"before" pattern not found, no changes made'
        ret['result'] = True
        return ret

    if __opts__['test']:
        ret['comment'] = 'File {0} is set to be updated'.format(name)
        ret['result'] = None
        return ret

    with salt.utils.fopen(name, 'rb') as fp_:
        slines = fp_.readlines()

    # should be ok now; perform the edit
    retcode = __salt__['file.sed'](path=name,
                                   before=before,
                                   after=after,
                                   limit=limit,
                                   backup=backup,
                                   options=options,
                                   flags=flags,
                                   negate_match=negate_match)['retcode']

    if retcode != 0:
        ret['result'] = False
        ret['comment'] = ('There was an error running sed.  '
                          'Return code {0}').format(retcode)
        return ret

    with salt.utils.fopen(name, 'rb') as fp_:
        nlines = fp_.readlines()

    if slines != nlines:
        if not salt.utils.istextfile(name):
            ret['changes']['diff'] = 'Replace binary file'
        else:
            # Changes happened, add them
            ret['changes']['diff'] = ''.join(difflib.unified_diff(slines,
                                                                  nlines))

            # Don't check the result -- sed is not designed to be able to check
            # the result, because of backreferences and so forth. Just report
            # that sed was run, and assume it was successful (no error!)
            ret['result'] = True
            ret['comment'] = 'sed ran without error'
    else:
        ret['result'] = True
        ret['comment'] = 'sed ran without error, but no changes were made'

    return ret