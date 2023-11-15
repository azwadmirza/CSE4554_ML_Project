def replace(name,
            pattern,
            repl,
            count=0,
            flags=0,
            bufsize=1,
            append_if_not_found=False,
            prepend_if_not_found=False,
            not_found_content=None,
            backup='.bak',
            show_changes=True):
    r'''
    Maintain an edit in a file

    .. versionadded:: 0.17.0

    Params are identical to the remote execution function :mod:`file.replace
    <salt.modules.file.replace>`.

    For complex regex patterns it can be useful to avoid the need for complex
    quoting and escape sequences by making use of YAML's multiline string
    syntax.

    .. code-block:: yaml

        complex_search_and_replace:
          file.replace:
            # <...snip...>
            - pattern: |
                CentOS \(2.6.32[^\n]+\n\s+root[^\n]+\n\)+
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
                                       append_if_not_found=append_if_not_found,
                                       prepend_if_not_found=prepend_if_not_found,
                                       not_found_content=not_found_content,
                                       backup=backup,
                                       dry_run=__opts__['test'],
                                       show_changes=show_changes)

    if changes:
        ret['changes'] = {'diff': changes}
        ret['comment'] = ('Changes were made'
                if not __opts__['test'] else 'Changes would have been made')
    else:
        ret['comment'] = 'No changes were made'

    ret['result'] = True if not __opts__['test'] else None
    return ret