def merge_networks(base, override):
    merged_networks = {}
    all_network_names = set(base) | set(override)
    base = {k: {} for k in base} if isinstance(base, list) else base
    override = {k: {} for k in override} if isinstance(override, list) else override
    for network_name in all_network_names:
        md = MergeDict(base.get(network_name, {}), override.get(network_name, {}))
        md.merge_field('aliases', merge_unique_items_lists, [])
        md.merge_field('link_local_ips', merge_unique_items_lists, [])
        md.merge_scalar('priority')
        md.merge_scalar('ipv4_address')
        md.merge_scalar('ipv6_address')
        merged_networks[network_name] = dict(md)
    return merged_networks