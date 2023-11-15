def other_package_info(info, desc):
    """Return information about another package supporting the device."""
    return "Found %s at %s, check %s" % (info.name, get_addr_from_info(info), desc)