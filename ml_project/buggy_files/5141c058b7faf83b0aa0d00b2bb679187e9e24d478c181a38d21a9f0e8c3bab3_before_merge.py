def _sunos_memdata():
    '''
    Return the memory information for SunOS-like systems
    '''
    grains = {'mem_total': 0, 'swap_total': 0}

    prtconf = '/usr/sbin/prtconf 2>/dev/null'
    for line in __salt__['cmd.run'](prtconf, python_shell=True).splitlines():
        comps = line.split(' ')
        if comps[0].strip() == 'Memory' and comps[1].strip() == 'size:':
            grains['mem_total'] = int(comps[2].strip())

    swap_cmd = salt.utils.path.which('swap')
    swap_total = __salt__['cmd.run']('{0} -s'.format(swap_cmd)).split()[1]
    grains['swap_total'] = int(swap_total) // 1024
    return grains