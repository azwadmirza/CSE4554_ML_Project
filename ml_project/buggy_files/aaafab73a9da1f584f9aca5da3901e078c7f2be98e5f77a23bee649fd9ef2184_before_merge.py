def mod_run_check(cmd_kwargs, onlyif, unless):
    '''
    Execute the onlyif and unless logic. Return a result dict if:

    * onlyif failed (onlyif != 0)
    * unless succeeded (unless == 0)

    Otherwise, returns ``True``
    '''
    cmd_kwargs = copy.deepcopy(cmd_kwargs)
    cmd_kwargs['python_shell'] = True
    if onlyif:
        if __salt__['cmd.retcode'](onlyif, **cmd_kwargs) != 0:
            return {'comment': 'onlyif condition is false',
                    'skip_watch': True,
                    'result': True}

    if unless:
        if __salt__['cmd.retcode'](unless, **cmd_kwargs) == 0:
            return {'comment': 'unless condition is true',
                    'skip_watch': True,
                    'result': True}

    # No reason to stop, return True
    return True