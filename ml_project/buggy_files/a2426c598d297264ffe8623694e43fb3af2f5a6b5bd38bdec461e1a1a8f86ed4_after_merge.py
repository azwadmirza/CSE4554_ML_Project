def _bsd_cpudata(osdata):
    '''
    Return CPU information for BSD-like systems
    '''
    # Provides:
    #   cpuarch
    #   num_cpus
    #   cpu_model
    #   cpu_flags
    sysctl = salt.utils.which('sysctl')
    arch = salt.utils.which('arch')
    cmds = {}

    if sysctl:
        cmds.update({
            'num_cpus': '{0} -n hw.ncpu'.format(sysctl),
            'cpuarch': '{0} -n hw.machine'.format(sysctl),
            'cpu_model': '{0} -n hw.model'.format(sysctl),
        })

    if arch and osdata['kernel'] == 'OpenBSD':
        cmds['cpuarch'] = '{0} -s'.format(arch)

    if osdata['kernel'] == 'Darwin':
        cmds['cpu_model'] = '{0} -n machdep.cpu.brand_string'.format(sysctl)
        cmds['cpu_flags'] = '{0} -n machdep.cpu.features'.format(sysctl)

    grains = dict([(k, __salt__['cmd.run'](v)) for k, v in cmds.items()])

    if 'cpu_flags' in grains and not isinstance(grains['cpu_flags'], list):
        grains['cpu_flags'] = grains['cpu_flags'].split(' ')

    if osdata['kernel'] == 'NetBSD':
        grains['cpu_flags'] = []
        for line in __salt__['cmd.run']('cpuctl identify 0').splitlines():
            m = re.match(r'cpu[0-9]:\ features[0-9]?\ .+<(.+)>', line)
            if m:
                flag = m.group(1).split(',')
                grains['cpu_flags'].extend(flag)

    if osdata['kernel'] == 'FreeBSD' and os.path.isfile('/var/run/dmesg.boot'):
        grains['cpu_flags'] = []
        # TODO: at least it needs to be tested for BSD other then FreeBSD
        with salt.utils.fopen('/var/run/dmesg.boot', 'r') as _fp:
            cpu_here = False
            for line in _fp:
                if line.startswith('CPU: '):
                    cpu_here = True  # starts CPU descr
                    continue
                if cpu_here:
                    if not line.startswith(' '):
                        break  # game over
                    if 'Features' in line:
                        start = line.find('<')
                        end = line.find('>')
                        if start > 0 and end > 0:
                            flag = line[start + 1:end].split(',')
                            grains['cpu_flags'].extend(flag)
    try:
        grains['num_cpus'] = int(grains['num_cpus'])
    except ValueError:
        grains['num_cpus'] = 1

    return grains