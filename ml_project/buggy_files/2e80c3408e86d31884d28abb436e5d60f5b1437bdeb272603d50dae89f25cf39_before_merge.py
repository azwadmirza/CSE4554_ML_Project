def traceroute(host):
    '''
    Performs a traceroute to a 3rd party host

    .. versionchanged:: 2015.8.0
        Added support for SunOS

    .. versionchanged:: 2016.11.4
        Added support for AIX

    CLI Example:

    .. code-block:: bash

        salt '*' network.traceroute archlinux.org
    '''
    ret = []
    if not salt.utils.path.which('traceroute'):
        log.info('This minion does not have traceroute installed')
        return ret

    cmd = 'traceroute {0}'.format(salt.utils.network.sanitize_host(host))

    out = __salt__['cmd.run'](cmd)

    # Parse version of traceroute
    if salt.utils.platform.is_sunos() or salt.utils.platform.is_aix():
        traceroute_version = [0, 0, 0]
    else:
        cmd2 = 'traceroute --version'
        out2 = __salt__['cmd.run'](cmd2)
        try:
            # Linux traceroute version looks like:
            #   Modern traceroute for Linux, version 2.0.19, Dec 10 2012
            # Darwin and FreeBSD traceroute version looks like: Version 1.4a12+[FreeBSD|Darwin]

            traceroute_version_raw = re.findall(r'.*[Vv]ersion (\d+)\.([\w\+]+)\.*(\w*)', out2)[0]
            log.debug('traceroute_version_raw: %s', traceroute_version_raw)
            traceroute_version = []
            for t in traceroute_version_raw:
                try:
                    traceroute_version.append(int(t))
                except ValueError:
                    traceroute_version.append(t)

            if len(traceroute_version) < 3:
                traceroute_version.append(0)

            log.debug('traceroute_version: %s', traceroute_version)

        except IndexError:
            traceroute_version = [0, 0, 0]

    for line in out.splitlines():
        if ' ' not in line:
            continue
        if line.startswith('traceroute'):
            continue

        if salt.utils.platform.is_aix():
            if line.startswith('trying to get source for'):
                continue

            if line.startswith('source should be'):
                continue

            if line.startswith('outgoing MTU'):
                continue

            if line.startswith('fragmentation required'):
                continue

        if 'Darwin' in six.text_type(traceroute_version[1]) or \
            'FreeBSD' in six.text_type(traceroute_version[1]) or \
                __grains__['kernel'] in ('SunOS', 'AIX'):
            try:
                traceline = re.findall(r'\s*(\d*)\s+(.*)\s+\((.*)\)\s+(.*)$', line)[0]
            except IndexError:
                traceline = re.findall(r'\s*(\d*)\s+(\*\s+\*\s+\*)', line)[0]

            log.debug('traceline: %s', traceline)
            delays = re.findall(r'(\d+\.\d+)\s*ms', six.text_type(traceline))

            try:
                if traceline[1] == '* * *':
                    result = {
                        'count': traceline[0],
                        'hostname': '*'
                    }
                else:
                    result = {
                        'count': traceline[0],
                        'hostname': traceline[1],
                        'ip': traceline[2],
                    }
                    for idx in range(0, len(delays)):
                        result['ms{0}'.format(idx + 1)] = delays[idx]
            except IndexError:
                result = {}

        elif (traceroute_version[0] >= 2 and traceroute_version[2] >= 14
                or traceroute_version[0] >= 2 and traceroute_version[1] > 0):
            comps = line.split('  ')
            if comps[1] == '* * *':
                result = {
                    'count': int(comps[0]),
                    'hostname': '*'}
            else:
                result = {
                    'count': int(comps[0]),
                    'hostname': comps[1].split()[0],
                    'ip': comps[1].split()[1].strip('()'),
                    'ms1': float(comps[2].split()[0]),
                    'ms2': float(comps[3].split()[0]),
                    'ms3': float(comps[4].split()[0])}
        else:
            comps = line.split()
            result = {
                'count': comps[0],
                'hostname': comps[1],
                'ip': comps[2],
                'ms1': comps[4],
                'ms2': comps[6],
                'ms3': comps[8],
                'ping1': comps[3],
                'ping2': comps[5],
                'ping3': comps[7]}

        ret.append(result)

    return ret