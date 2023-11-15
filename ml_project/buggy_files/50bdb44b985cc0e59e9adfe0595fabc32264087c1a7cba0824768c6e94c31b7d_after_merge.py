def canonical_channel_name(channel):
    if channel is None:
        return '<unknown>'
    channel = remove_binstar_tokens(channel).rstrip('/')
    if any(channel.startswith(i) for i in get_default_urls()):
        return 'defaults'
    elif any(channel.startswith(i) for i in get_local_urls(clear_cache=False)):
        return 'local'
    elif channel.startswith('http://filer/'):
        return 'filer'
    elif channel.startswith(channel_alias):
        return channel.split(channel_alias, 1)[1]
    elif channel.startswith('http:/'):
        channel2 = 'https' + channel[4:]
        channel3 = canonical_channel_name(channel2)
        return channel3 if channel3 != channel2 else channel
    else:
        return channel