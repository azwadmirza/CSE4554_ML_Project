def is_proxytype(opts, proxytype):
    """
    Is this a proxy minion of type proxytype
    """
    return (
        salt.utils.platform.is_proxy()
        and opts.get("proxy", None).get("proxytype", None) == proxytype
    )