def other_package_info(info, desc):
    """Return information about another package supporting the device."""
    return "%s @ %s, check %s" % (info.name, ipaddress.ip_address(info.address), desc)