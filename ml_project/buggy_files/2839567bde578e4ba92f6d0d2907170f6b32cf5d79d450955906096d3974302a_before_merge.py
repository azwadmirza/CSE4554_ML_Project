def _get_hosts_from_group(group):
    inventory = __context__["inventory"]
    hosts = [host for host in inventory[group].get("hosts", [])]
    for child in inventory[group].get("children", []):
        if child != "ungrouped":
            hosts.extend(_get_hosts_from_group(child))
        hosts.extend(_get_hosts_from_group(child))
    return hosts