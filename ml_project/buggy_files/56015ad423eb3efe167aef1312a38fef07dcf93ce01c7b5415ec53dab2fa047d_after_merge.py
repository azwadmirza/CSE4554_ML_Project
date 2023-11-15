def _netstat_route_netbsd():
    '''
    Return netstat routing information for NetBSD
    '''
    ret = []
    cmd = 'netstat -f inet -rn | tail -n+5'
    out = __salt__['cmd.run'](cmd, python_shell=True)
    for line in out.splitlines():
        comps = line.split()
        ret.append({
            'addr_family': 'inet',
            'destination': comps[0],
            'gateway': comps[1],
            'netmask': '',
            'flags': comps[3],
            'interface': comps[6]})
    cmd = 'netstat -f inet6 -rn | tail -n+5'
    out = __salt__['cmd.run'](cmd, python_shell=True)
    for line in out.splitlines():
        comps = line.split()
        ret.append({
            'addr_family': 'inet6',
            'destination': comps[0],
            'gateway': comps[1],
            'netmask': '',
            'flags': comps[3],
            'interface': comps[6]})
    return ret