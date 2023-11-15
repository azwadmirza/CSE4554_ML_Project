def __virtual__():
    if salt.utils.platform.is_proxy() and 'proxy' in __opts__ and __opts__['proxy'].get('proxytype') == 'fx2':
        return __virtualname__
    return False