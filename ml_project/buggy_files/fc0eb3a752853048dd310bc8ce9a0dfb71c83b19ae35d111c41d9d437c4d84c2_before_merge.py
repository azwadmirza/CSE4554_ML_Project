def _netstat_route_openbsd():
    '''
    Return netstat routing information for OpenBSD
    '''
    ret = []
    cmd = 'netstat -f inet -rn | tail -n+5'
    out = __salt__['cmd.run'](cmd)
    for line in out.splitlines():
        comps = line.split()
        ret.append({
            'addr_family': 'inet',
            'destination': comps[0],
            'gateway': comps[1],
            'netmask': '',
            'flags': comps[2],
            'interface': comps[7]})
    cmd = 'netstat -f inet6 -rn | tail -n+5'
    out = __salt__['cmd.run'](cmd)
    for line in out.splitlines():
        comps = line.split()
        ret.append({
            'addr_family': 'inet6',
            'destination': comps[0],
            'gateway': comps[1],
            'netmask': '',
            'flags': comps[2],
            'interface': comps[7]})
    return ret