def _srvmgr(func):
    '''
    Execute a function from the ServerManager PS module and return the STDOUT
    '''
    return __salt__['cmd.run']('Import-Module ServerManager ; {0}'.format(func), shell='powershell')