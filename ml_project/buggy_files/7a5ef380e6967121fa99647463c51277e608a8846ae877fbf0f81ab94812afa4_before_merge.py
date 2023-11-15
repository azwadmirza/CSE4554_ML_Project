def __virtual__():
    '''
    Only work on select distros which still use Red Hat's /usr/bin/service for
    management of either sysvinit or a hybrid sysvinit/upstart init system.
    '''
    # Enable on these platforms only.
    enable = set((
        'XenServer',
        'RedHat',
        'CentOS',
        'ScientificLinux',
        'CloudLinux',
        'Amazon',
        'Fedora',
        'ALT',
        'OEL',
        'SUSE  Enterprise Server',
        'SUSE',
        'McAfee  OS Server'
    ))
    if __grains__['os'] in enable:
        if __grains__['os'] == 'XenServer':
            return __virtualname__
        try:
            osrelease = float(__grains__.get('osrelease', 0))
        except ValueError:
            return (False, 'Cannot load rh_service module: '
                           'osrelease grain, {0}, not a float,'.format(osrelease))
        if __grains__['os'] == 'SUSE':
            if osrelease >= 12:
                return (False, 'Cannot load rh_service module on SUSE >= 12')
        if __grains__['os'] == 'Fedora':
            if osrelease > 15:
                return (False, 'Cannot load rh_service module on Fedora >= 15')
        if __grains__['os'] in ('RedHat', 'CentOS', 'ScientificLinux', 'OEL'):
            if osrelease >= 7:
                return (False, 'Cannot load rh_service module on RedHat >= 7')
        return __virtualname__
    return (False, 'Cannot load rh_service module: OS not in {0}'.format(enable))