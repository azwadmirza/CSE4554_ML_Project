def ip_fqdn():
    """
    Return ip address and FQDN grains
    """
    if salt.utils.platform.is_proxy():
        return {}

    ret = {}
    ret["ipv4"] = salt.utils.network.ip_addrs(include_loopback=True)
    ret["ipv6"] = salt.utils.network.ip_addrs6(include_loopback=True)

    _fqdn = hostname()["fqdn"]
    for socket_type, ipv_num in ((socket.AF_INET, "4"), (socket.AF_INET6, "6")):
        key = "fqdn_ip" + ipv_num
        if not ret["ipv" + ipv_num]:
            ret[key] = []
        else:
            try:
                start_time = datetime.datetime.utcnow()
                info = socket.getaddrinfo(_fqdn, None, socket_type)
                ret[key] = list(set(item[4][0] for item in info))
            except (socket.error, UnicodeError):
                timediff = datetime.datetime.utcnow() - start_time
                if timediff.seconds > 5 and __opts__["__role"] == "master":
                    log.warning(
                        'Unable to find IPv%s record for "%s" causing a %s '
                        "second timeout when rendering grains. Set the dns or "
                        "/etc/hosts for IPv%s to clear this.",
                        ipv_num,
                        _fqdn,
                        timediff,
                        ipv_num,
                    )
                ret[key] = []

    return ret