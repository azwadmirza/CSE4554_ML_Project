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
    cmd = 'traceroute {0}'.format(salt.utils.network.sanitize_host(host))
    out = __salt__['cmd.run'](cmd)

    # Parse version of traceroute
    if salt.utils.platform.is_sunos() or salt.utils.platform.is_aix():
        traceroute_version = [0, 0, 0]
    else:
        version_out = __salt__['cmd.run']('traceroute --version')
        try:
            # Linux traceroute version looks like:
            #   Modern traceroute for Linux, version 2.0.19, Dec 10 2012
            # Darwin and FreeBSD traceroute version looks like: Version 1.4a12+[FreeBSD|Darwin]

            version_raw = re.findall(r'.*[Vv]ersion (\d+)\.([\w\+]+)\.*(\w*)', version_out)[0]
            log.debug('traceroute_version_raw: %s', version_raw)
            traceroute_version = []
            for t in version_raw:
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
        # Pre requirements for line parsing
        skip_line = False
        if ' ' not in line:
            skip_line = True
        if line.startswith('traceroute'):
            skip_line = True
        if salt.utils.platform.is_aix():
            if line.startswith('trying to get source for'):
                skip_line = True
            if line.startswith('source should be'):
                skip_line = True
            if line.startswith('outgoing MTU'):
                skip_line = True
            if line.startswith('fragmentation required'):
                skip_line = True
        if skip_line:
            log.debug('Skipping traceroute output line: %s', line)
            continue

        # Parse output from unix variants
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

        # Parse output from specific version ranges
        elif (traceroute_version[0] >= 2 and traceroute_version[2] >= 14
                or traceroute_version[0] >= 2 and traceroute_version[1] > 0):
            comps = line.split('  ')
            if len(comps) >= 2 and comps[1] == '* * *':
                result = {
                    'count': int(comps[0]),
                    'hostname': '*'}
            elif len(comps) >= 5:
                result = {
                    'count': int(comps[0]),
                    'hostname': comps[1].split()[0],
                    'ip': comps[1].split()[1].strip('()'),
                    'ms1': float(comps[2].split()[0]),
                    'ms2': float(comps[3].split()[0]),
                    'ms3': float(comps[4].split()[0])}
            else:
                result = {}

        # Parse anything else
        else:
            comps = line.split()
            if len(comps) >= 8:
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
            else:
                result = {}

        ret.append(result)
        if not result:
            log.warn('Cannot parse traceroute output line: %s', line)
    return ret