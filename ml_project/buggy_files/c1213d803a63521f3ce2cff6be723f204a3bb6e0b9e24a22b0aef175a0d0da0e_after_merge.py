def __virtual__():
    '''
    Only works on Windows systems
    '''
    if not salt.utils.platform.is_windows():
        return False, 'Module win_dns_client: module only works on Windows ' \
                      'systems'
    if not HAS_LIBS:
        return False, 'Module win_dns_client: missing required libraries'
    return 'win_dns_client'