def replace(name,
            pattern,
            repl,
            count=0,
            flags=0,
            bufsize=1,
            backup='.bak',
            show_changes=True):
    '''
    Maintain an edit in a file

    .. versionadded:: 0.17

    Params are identical to :py:func:`~salt.modules.file.replace`.

    '''
    ret = {'name': name, 'changes': {}, 'result': False, 'comment': ''}

    check_res, check_msg = _check_file(name)
    if not check_res:
        return _error(ret, check_msg)

    changes = __salt__['file.replace'](name,
                                       pattern,
                                       repl,
                                       count=count,
                                       flags=flags,
                                       bufsize=bufsize,
                                       backup=backup,
                                       dry_run=__opts__['test'],
                                       show_changes=show_changes)

    if changes:
        ret['changes'] = changes
        ret['comment'] = 'Changes were made'
    else:
        ret['comment'] = 'No changes were made'

    ret['result'] = True
    return ret