def url_channel(url):
    parts = (url or '').rsplit('/', 2)
    if len(parts) == 1:
        return '<unknown>', '<unknown>'
    if len(parts) == 2:
        return parts[0], parts[0]
    if url.startswith('file://') and parts[1] not in ('noarch', subdir):
        # Explicit file-based URLs are denoted with a '/' in the schannel
        channel = parts[0] + '/' + parts[1]
        schannel = channel + '/'
    else:
        channel = parts[0]
        schannel = canonical_channel_name(channel)
    return channel, schannel