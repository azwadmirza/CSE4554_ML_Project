def __virtual__():
    if not salt.utils.platform.is_proxy() or 'proxy' not in __opts__:
        return False
    else:
        return __virtualname__