def get_route(ip):
    '''
    Return routing information for given destination ip

    .. versionadded:: 2015.5.3

    .. versionchanged:: 2015.8.0
        Added support for SunOS (Solaris 10, Illumos, SmartOS)
        Added support for OpenBSD

    .. versionchanged:: 2016.11.4
        Added support for AIX

    CLI Example::

        salt '*' network.get_route 10.10.10.10
    '''

    if __grains__['kernel'] == 'Linux':
        cmd = 'ip route get {0}'.format(ip)
        out = __salt__['cmd.run'](cmd, python_shell=True)
        regexp = re.compile(r'(via\s+(?P<gateway>[\w\.:]+))?\s+dev\s+(?P<interface>[\w\.\:]+)\s+.*src\s+(?P<source>[\w\.:]+)')
        m = regexp.search(out.splitlines()[0])
        ret = {
            'destination': ip,
            'gateway': m.group('gateway'),
            'interface': m.group('interface'),
            'source': m.group('source')
        }

        return ret

    if __grains__['kernel'] == 'SunOS':
        # [root@nacl ~]# route -n get 172.16.10.123
        #   route to: 172.16.10.123
        #destination: 172.16.10.0
        #       mask: 255.255.255.0
        #  interface: net0
        #      flags: <UP,DONE,KERNEL>
        # recvpipe  sendpipe  ssthresh    rtt,ms rttvar,ms  hopcount      mtu     expire
        #       0         0         0         0         0         0      1500         0
        cmd = '/usr/sbin/route -n get {0}'.format(ip)
        out = __salt__['cmd.run'](cmd, python_shell=False)

        ret = {
            'destination': ip,
            'gateway': None,
            'interface': None,
            'source': None
        }

        for line in out.splitlines():
            line = line.split(':')
            if 'route to' in line[0]:
                ret['destination'] = line[1].strip()
            if 'gateway' in line[0]:
                ret['gateway'] = line[1].strip()
            if 'interface' in line[0]:
                ret['interface'] = line[1].strip()
                ret['source'] = salt.utils.network.interface_ip(line[1].strip())

        return ret

    if __grains__['kernel'] == 'OpenBSD':
        # [root@exosphere] route -n get blackdot.be
        #   route to: 5.135.127.100
        #destination: default
        #       mask: default
        #    gateway: 192.168.0.1
        #  interface: vio0
        # if address: 192.168.0.2
        #   priority: 8 (static)
        #      flags: <UP,GATEWAY,DONE,STATIC>
        #     use       mtu    expire
        # 8352657         0         0
        cmd = 'route -n get {0}'.format(ip)
        out = __salt__['cmd.run'](cmd, python_shell=False)

        ret = {
            'destination': ip,
            'gateway': None,
            'interface': None,
            'source': None
        }

        for line in out.splitlines():
            line = line.split(':')
            if 'route to' in line[0]:
                ret['destination'] = line[1].strip()
            if 'gateway' in line[0]:
                ret['gateway'] = line[1].strip()
            if 'interface' in line[0]:
                ret['interface'] = line[1].strip()
            if 'if address' in line[0]:
                ret['source'] = line[1].strip()

        return ret

    if __grains__['kernel'] == 'AIX':
        # root@la68pp002_pub:~# route -n get 172.29.149.95
        #   route to: 172.29.149.95
        #destination: 172.29.149.95
        #    gateway: 127.0.0.1
        #  interface: lo0
        #interf addr: 127.0.0.1
        #     flags: <UP,GATEWAY,HOST,DONE,STATIC>
        #recvpipe  sendpipe  ssthresh  rtt,msec    rttvar  hopcount      mtu     expire
        #      0         0         0         0         0         0         0    -68642
        cmd = 'route -n get {0}'.format(ip)
        out = __salt__['cmd.run'](cmd, python_shell=False)

        ret = {
            'destination': ip,
            'gateway': None,
            'interface': None,
            'source': None
        }

        for line in out.splitlines():
            line = line.split(':')
            if 'route to' in line[0]:
                ret['destination'] = line[1].strip()
            if 'gateway' in line[0]:
                ret['gateway'] = line[1].strip()
            if 'interface' in line[0]:
                ret['interface'] = line[1].strip()
            if 'interf addr' in line[0]:
                ret['source'] = line[1].strip()

        return ret

    else:
        raise CommandExecutionError('Not yet supported on this platform')