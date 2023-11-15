def format_address(address: typing.Optional[tuple]) -> str:
    """
    This function accepts IPv4/IPv6 tuples and
    returns the formatted address string with port number
    """
    if address is None:
        return "<no address>"
    try:
        host = ipaddress.ip_address(address[0])
        if host.is_unspecified:
            return "*:{}".format(address[1])
        if isinstance(host, ipaddress.IPv4Address):
            return "{}:{}".format(str(host), address[1])
        # If IPv6 is mapped to IPv4
        elif host.ipv4_mapped:
            return "{}:{}".format(str(host.ipv4_mapped), address[1])
        return "[{}]:{}".format(str(host), address[1])
    except ValueError:
        return "{}:{}".format(address[0], address[1])