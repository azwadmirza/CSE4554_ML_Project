def get_index(channel_urls=(), prepend=True, platform=None,
              use_local=False, use_cache=False, unknown=False,
              offline=False, prefix=None):
    """
    Return the index of packages available on the channels

    If prepend=False, only the channels passed in as arguments are used.
    If platform=None, then the current platform is used.
    If prefix is supplied, then the packages installed in that prefix are added.
    """
    if use_local:
        channel_urls = ['local'] + list(channel_urls)
    channel_urls = normalize_urls(channel_urls, platform, offline)
    if prepend:
        channel_urls.extend(get_channel_urls(platform, offline))
    channel_urls = prioritize_channels(channel_urls)
    index = fetch_index(channel_urls, use_cache=use_cache, unknown=unknown)
    if prefix:
        priorities = {c: p for c, p in itervalues(channel_urls)}
        for dist, info in iteritems(install.linked_data(prefix)):
            fn = info['fn']
            schannel = info['schannel']
            prefix = '' if schannel == 'defaults' else schannel + '::'
            priority = priorities.get(schannel, 0)
            key = prefix + fn
            if key in index:
                # Copy the link information so the resolver knows this is installed
                index[key]['link'] = info.get('link')
            else:
                # only if the package in not in the repodata, use local
                # conda-meta (with 'depends' defaulting to [])
                info.setdefault('depends', [])
                info['priority'] = priority
                index[key] = info
    return index