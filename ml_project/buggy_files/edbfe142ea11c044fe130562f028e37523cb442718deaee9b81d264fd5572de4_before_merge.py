def install(feature, recurse=False):
    '''
    Install a feature

    Note:
    Some features requires reboot after un/installation, if so until the server is restarted
    Other features can not be installed !

    Note:
    Some features takes a long time to complete un/installation, set -t with a long timeout

    CLI Example:

    .. code-block:: bash

        salt '*' win_servermanager.install Telnet-Client
        salt '*' win_servermanager.install SNMP-Services True
    '''
    sub = ''
    if recurse:
        sub = '-IncludeAllSubFeature'
    out = _srvmgr('Add-WindowsFeature -Name {0} {1} -erroraction silentlycontinue | format-list'.format(feature, sub))
    return _parse_powershell_list(out)