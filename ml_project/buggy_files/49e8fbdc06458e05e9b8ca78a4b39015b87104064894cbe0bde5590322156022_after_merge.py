def enable():
    '''
    Enable RDP the service on the server

    CLI Example:

    .. code-block:: bash

        salt '*' rdp.enable
    '''

    return _parse_return_code_powershell(
        _psrdp('$RDP.SetAllowTsConnections(1,1)')) == 0