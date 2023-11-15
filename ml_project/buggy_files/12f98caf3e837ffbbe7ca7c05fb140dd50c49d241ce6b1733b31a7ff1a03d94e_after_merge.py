def get_disabled():
    '''
    Return the disabled services

    CLI Example:

    .. code-block:: bash

        salt '*' service.get_disabled
    '''
    if has_powershell():
        cmd = 'Get-WmiObject win32_service | where {$_.startmode -ne "Auto"} | select-object name'
        lines = __salt__['cmd.run'](cmd, shell='POWERSHELL').splitlines()
        return sorted([line.strip() for line in lines[3:]])
    else:
        ret = set()
        services = []
        cmd = list2cmdline(['sc', 'query', 'type=', 'service', 'state=', 'all', 'bufsize=', str(BUFFSIZE)])
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
                if 'DEMAND_START' in line:
                    ret.add(service)
                elif 'DISABLED' in line:
                    ret.add(service)
        return sorted(ret)