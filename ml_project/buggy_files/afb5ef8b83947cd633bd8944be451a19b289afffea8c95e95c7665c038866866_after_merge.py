def __virtual__():

    try:
        if salt.utils.is_proxy() and __opts__['proxy']['proxytype'] == 'esxi':
            return __virtualname__
    except KeyError:
        pass

    return False