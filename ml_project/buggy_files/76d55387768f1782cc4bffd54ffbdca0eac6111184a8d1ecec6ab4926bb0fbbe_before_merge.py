def check_remote_network_config(remote, local):
    if local.driver and remote.get('Driver') != local.driver:
        raise NetworkConfigChangedError(local.true_name, 'driver')
    local_opts = local.driver_opts or {}
    remote_opts = remote.get('Options') or {}
    for k in set.union(set(remote_opts.keys()), set(local_opts.keys())):
        if k in OPTS_EXCEPTIONS:
            continue
        if remote_opts.get(k) != local_opts.get(k):
            raise NetworkConfigChangedError(local.true_name, 'option "{}"'.format(k))

    if local.ipam is not None:
        check_remote_ipam_config(remote, local)

    if local.internal is not None and local.internal != remote.get('Internal', False):
        raise NetworkConfigChangedError(local.true_name, 'internal')
    if local.enable_ipv6 is not None and local.enable_ipv6 != remote.get('EnableIPv6', False):
        raise NetworkConfigChangedError(local.true_name, 'enable_ipv6')

    local_labels = local.labels or {}
    remote_labels = remote.get('Labels', {})
    for k in set.union(set(remote_labels.keys()), set(local_labels.keys())):
        if k.startswith('com.docker.'):  # We are only interested in user-specified labels
            continue
        if remote_labels.get(k) != local_labels.get(k):
            log.warning(
                'Network {}: label "{}" has changed. It may need to be'
                ' recreated.'.format(local.true_name, k)
            )