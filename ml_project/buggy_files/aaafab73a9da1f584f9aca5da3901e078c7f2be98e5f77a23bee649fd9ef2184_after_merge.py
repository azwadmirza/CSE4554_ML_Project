def mod_run_check(cmd_kwargs, onlyif, unless):
    '''
    Execute the onlyif and unless logic. Return a result dict if:

    * onlyif failed (onlyif != 0)
    * unless succeeded (unless == 0)

    Otherwise, returns ``True``
    '''
    cmd_kwargs = copy.deepcopy(cmd_kwargs)
    cmd_kwargs.update({
        'use_vt': False,
        'bg': False,
        'ignore_retcode': True,
        'python_shell': True,
    })

    if onlyif is not None:
        if not isinstance(onlyif, list):
            onlyif = [onlyif]

        for command in onlyif:
            if not isinstance(command, six.string_types) and command:
                # Boolean or some other non-string which resolves to True
                continue
            try:
                if __salt__['cmd.retcode'](command, **cmd_kwargs) == 0:
                    # Command exited with a zero retcode
                    continue
            except Exception as exc:
                log.exception(
                    'The following onlyif command raised an error: %s',
                    command
                )
                return {
                    'comment': 'onlyif raised error ({0}), see log for '
                               'more details'.format(exc),
                    'result': False
                }

            return {'comment': 'onlyif condition is false',
                    'skip_watch': True,
                    'result': True}

    if unless is not None:
        if not isinstance(unless, list):
            unless = [unless]

        for command in unless:
            if not isinstance(command, six.string_types) and not command:
                # Boolean or some other non-string which resolves to False
                break
            try:
                if __salt__['cmd.retcode'](command, **cmd_kwargs) != 0:
                    # Command exited with a non-zero retcode
                    break
            except Exception as exc:
                log.exception(
                    'The following unless command raised an error: %s',
                    command
                )
                return {
                    'comment': 'unless raised error ({0}), see log for '
                               'more details'.format(exc),
                    'result': False
                }
        else:
            return {'comment': 'unless condition is true',
                    'skip_watch': True,
                    'result': True}

    return True