def get_enabled():
    '''
    Return the enabled services

    CLI Example:

    .. code-block:: bash

        salt '*' service.get_enabled
    '''

    if has_powershell():
        cmd = 'Get-WmiObject win32_service | where {$_.startmode -eq "Auto"} | select-object name'
        lines = __salt__['cmd.run'](cmd, shell='POWERSHELL').splitlines()
        return sorted([line.strip() for line in lines[3:]])
    else:
        ret = set()
        services = []
        cmd = 'sc query type= service state= all bufsize= {0}'.format(BUFFSIZE)
        lines = __salt__['cmd.run'](cmd).splitlines()
        for line in lines:
            if 'SERVICE_NAME:' in line:
                comps = line.split(':', 1)
                if not len(comps) > 1:
                    continue
                services.append(comps[1].strip())
        for service in services:
            cmd2 = list2cmdline(['sc', 'qc', service, BUFFSIZE])
            lines = __salt__['cmd.run'](cmd2).splitlines()
            for line in lines:
                if 'AUTO_START' in line:
                    ret.add(service)
        return sorted(ret)