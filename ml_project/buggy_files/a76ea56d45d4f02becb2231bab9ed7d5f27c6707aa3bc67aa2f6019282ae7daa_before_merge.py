def status():
    '''
    Show if rdp is enabled on the server

    CLI Example:

    .. code-block:: bash

        salt '*' rdp.status
    '''

    cmd = '-InputFormat None -Command "& { $RDP = Get-WmiObject -Class Win32_TerminalServiceSetting -Namespace root\\CIMV2\\TerminalServices -Computer . -Authentication 6 -ErrorAction Stop ; echo $RDP.AllowTSConnections }"'
    cmd = '{0} {1}'.format(POWERSHELL, cmd)
    out = int(__salt__['cmd.run'](cmd).strip())
    return out != 0