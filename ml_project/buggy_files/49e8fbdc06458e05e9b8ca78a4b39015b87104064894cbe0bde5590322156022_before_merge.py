def enable():
    '''
    Enable RDP the service on the server

    CLI Example:

    .. code-block:: bash

        salt '*' rdp.enable
    '''

    cmd = '-InputFormat None -Command "& { $RDP = Get-WmiObject -Class Win32_TerminalServiceSetting -Namespace root\\CIMV2\\TerminalServices -Computer . -Authentication 6 -ErrorAction Stop ; $RDP.SetAllowTsConnections(1,1) }"'
    cmd = '{0} {1}'.format(POWERSHELL, cmd)
    return _parse_return_code_powershell(__salt__['cmd.run'](cmd)) == 0