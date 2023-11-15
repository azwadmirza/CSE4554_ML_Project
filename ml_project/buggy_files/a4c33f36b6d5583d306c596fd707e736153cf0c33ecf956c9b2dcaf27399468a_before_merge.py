def url_channel(url):
    if url is None:
        return None, '<unknown>'
    channel = url.rsplit('/', 2)[0]
    schannel = canonical_channel_name(channel)
    if url.startswith('file://') and schannel != 'local':
        channel = schannel = url.rsplit('/', 1)[0]
    return channel, schannel