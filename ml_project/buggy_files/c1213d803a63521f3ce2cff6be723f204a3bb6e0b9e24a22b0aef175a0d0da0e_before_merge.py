def __virtual__():
    '''
    Only works on Windows systems
    '''
    if salt.utils.platform.is_windows():
        return 'win_dns_client'
    return (False, "Module win_dns_client: module only works on Windows systems")