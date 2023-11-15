def _pecl(command):
    '''
    Execute the command passed with pecl
    '''
    cmdline = 'pecl {0}'.format(command)

    ret = __salt__['cmd.run_all'](cmdline)

    if ret['retcode'] == 0:
        return ret['stdout']
    else:
        return False