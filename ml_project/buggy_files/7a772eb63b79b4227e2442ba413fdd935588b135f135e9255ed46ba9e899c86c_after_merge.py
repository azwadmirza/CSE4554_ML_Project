def _linux_bin_exists(binary):
    '''
    Does a binary exist in linux (depends on which, type, or whereis)
    '''
    for search_cmd in ('which', 'type -ap'):
        try:
            return __salt__['cmd.retcode'](
                '{0} {1}'.format(search_cmd, binary)
            ) == 0
        except salt.exceptions.CommandExecutionError:
            pass

    try:
        return len(__salt__['cmd.run_all'](
            'whereis -b {0}'.format(binary)
        )['stdout'].split()) > 1
    except salt.exceptions.CommandExecutionError:
        return False