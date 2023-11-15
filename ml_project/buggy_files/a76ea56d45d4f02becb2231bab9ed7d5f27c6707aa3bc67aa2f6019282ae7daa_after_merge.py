def status():
    '''
    Show if rdp is enabled on the server

    CLI Example:

    .. code-block:: bash

        salt '*' rdp.status
    '''

    out = int(_psrdp('echo $RDP.AllowTSConnections').strip())
    return out != 0