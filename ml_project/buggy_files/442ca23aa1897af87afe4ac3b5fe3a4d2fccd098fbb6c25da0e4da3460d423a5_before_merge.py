def _find_set_info(set):
    '''
    Return information about the set
    '''

    cmd = '{0} list -t {1}'.format(_ipset_cmd(), set)
    out = __salt__['cmd.run_all'](cmd, python_shell=False)

    if out['retcode'] > 0:
        # Set doesn't exist return false
        return False

    setinfo = {}
    _tmp = out['stdout'].split('\n')
    for item in _tmp:
        key, value = item.split(':', 1)
        setinfo[key] = value[1:]
    return setinfo