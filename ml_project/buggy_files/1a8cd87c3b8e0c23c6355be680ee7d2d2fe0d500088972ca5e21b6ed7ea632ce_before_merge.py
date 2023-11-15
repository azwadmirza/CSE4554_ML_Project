def _windows_wwns():
    '''
    Return Fibre Channel port WWNs from a Windows host.
    '''
    ps_cmd = r'Get-WmiObject -class MSFC_FibrePortHBAAttributes -namespace "root\WMI" | Select -Expandproperty Attributes | %{($_.PortWWN | % {"{0:x2}" -f $_}) -join ""}'

    ret = []

    cmdret = __salt__['cmd.run_ps'](ps_cmd)

    for line in cmdret:
        ret.append(line.rstrip())

    return ret