def __virtual__():
    '''
    Confirm this module is on a Debian based system
    '''
    if __grains__.get('os_family') in ('Kali', 'Debian'):
        return __virtualname__
    return False