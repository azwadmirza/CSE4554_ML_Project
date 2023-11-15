def __virtual__():
    '''
    Confirm this module is on a Debian based system
    '''
    if __grains__.get('os_family') in ('Kali', 'Debian', 'LinuxMint'):
        return __virtualname__
    elif __grains__.get('os_family', False) == 'Cumulus':
        return __virtualname__
    return (False, 'The pkg module could not be loaded: unsupported OS family')