def __virtual__():
    '''
    Only work on systems which exclusively use sysvinit
    '''
    # Disable on these platforms, specific service modules exist:
    disable = set((
        'RedHat',
        'CentOS',
        'Amazon',
        'ScientificLinux',
        'CloudLinux',
        'Fedora',
        'Gentoo',
        'Ubuntu',
        'Debian',
        'Devuan',
        'Arch',
        'Arch ARM',
        'ALT',
        'SUSE  Enterprise Server',
        'SUSE',
        'OEL',
        'Linaro',
        'elementary OS',
        'McAfee  OS Server',
        'Void',
        'Mint',
        'Raspbian'
    ))
    if __grains__.get('os', '') in disable:
        return (False, 'Your OS is on the disabled list')
    # Disable on all non-Linux OSes as well
    if __grains__['kernel'] != 'Linux':
        return (False, 'Non Linux OSes are not supported')
    # Suse >=12.0 uses systemd
    if __grains__.get('os_family', '') == 'Suse':
        try:
            # osrelease might be in decimal format (e.g. "12.1"), or for
            # SLES might include service pack (e.g. "11 SP3"), so split on
            # non-digit characters, and the zeroth element is the major
            # number (it'd be so much simpler if it was always "X.Y"...)
            import re
            if int(re.split(r'\D+', __grains__.get('osrelease', ''))[0]) >= 12:
                return (False, 'Suse version greater than or equal to 12 is not supported')
        except ValueError:
            return (False, 'You are missing the os_family grain')
    return 'service'