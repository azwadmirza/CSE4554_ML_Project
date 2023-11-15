def _osx_memdata():
    '''
    Return the memory information for BSD-like systems
    '''
    grains = {'mem_total': 0, 'swap_total': 0}

    sysctl = salt.utils.path.which('sysctl')
    if sysctl:
        mem = __salt__['cmd.run']('{0} -n hw.memsize'.format(sysctl))
        swap_total = __salt__['cmd.run']('{0} -n vm.swapusage'.format(sysctl)).split()[2]
        if swap_total.endswith('K'):
            _power = 2**10
        elif swap_total.endswith('M'):
            _power = 2**20
        elif swap_total.endswith('G'):
            _power = 2**30
        swap_total = float(swap_total[:-1]) * _power

        grains['mem_total'] = int(mem) // 1024 // 1024
        grains['swap_total'] = int(swap_total) // 1024 // 1024
    return grains