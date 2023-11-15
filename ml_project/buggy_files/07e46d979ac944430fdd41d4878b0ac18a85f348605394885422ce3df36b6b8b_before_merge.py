def _netstat_route_linux():
    '''
    Return netstat routing information for Linux distros
    '''
    ret = []
    cmd = 'netstat -A inet -rn | tail -n+3'
    out = __salt__['cmd.run'](cmd)
    for line in out.splitlines():
        comps = line.split()
        ret.append({
            'addr_family': 'inet',
            'destination': comps[0],
            'gateway': comps[1],
            'netmask': comps[2],
            'flags': comps[3],
            'interface': comps[7]})
    cmd = 'netstat -A inet6 -rn | tail -n+3'
    out = __salt__['cmd.run'](cmd)
    for line in out.splitlines():
        comps = line.split()
        if len(comps) == 6:
            ret.append({
                'addr_family': 'inet6',
                'destination': comps[0],
                'gateway': comps[1],
                'netmask': '',
                'flags': comps[3],
                'interface': comps[5]})
        elif len(comps) == 7:
            ret.append({
                'addr_family': 'inet6',
                'destination': comps[0],
                'gateway': comps[1],
                'netmask': '',
                'flags': comps[3],
                'interface': comps[6]})
        else:
            continue
    return ret