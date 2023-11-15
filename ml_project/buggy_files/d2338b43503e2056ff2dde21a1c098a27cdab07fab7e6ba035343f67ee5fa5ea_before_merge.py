def _change_source_state(name, state):
    '''
    Instructs Chocolatey to change the state of a source.

    name
        Name of the repository to affect.

    state
        State in which you want the chocolatey repository.

    '''
    choc_path = _find_chocolatey(__context__, __salt__)
    cmd = [choc_path, 'source', state, '--name', name]
    result = __salt__['cmd.run_all'](cmd, python_shell=False)

    if result['retcode'] != 0:
        err = 'Running chocolatey failed: {0}'.format(result['stdout'])
        raise CommandExecutionError(err)

    return result['stdout']