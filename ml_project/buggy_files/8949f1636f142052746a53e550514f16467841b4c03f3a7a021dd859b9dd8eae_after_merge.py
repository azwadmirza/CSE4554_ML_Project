def disable():
    '''
    Disable RDP the service on the server

    CLI Example:

    .. code-block:: bash

        salt '*' rdp.disable
    '''

    return _parse_return_code_powershell(
        _psrdp('$RDP.SetAllowTsConnections(0,1)')) == 0