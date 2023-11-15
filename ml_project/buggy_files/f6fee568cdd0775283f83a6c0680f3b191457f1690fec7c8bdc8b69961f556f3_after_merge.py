def get_ip_from_name(ifname, v6=False):
    """Backward compatibility: indirectly calls get_ips
    Deprecated."""
    return get_ips(v6=v6).get(ifname, "")[0]