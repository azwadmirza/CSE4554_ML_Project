def _srvmgr(func):
    '''
    Execute a function from the ServerManager PS module and return the STDOUT
    '''
    return __salt__['cmd.run']('powershell -InputFormat None -Command "& {{ Import-Module ServerManager ; {0} }}"'.format(func))