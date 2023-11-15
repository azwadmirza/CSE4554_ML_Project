def __virtual__():
    if not salt.utils.is_proxy():
        return False
    else:
        return __virtualname__