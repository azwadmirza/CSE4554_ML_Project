def _read_channel_configuration(scheme, host, port, path):
    # return location, name, scheme, auth, token

    path = path and path.rstrip('/')
    test_url = Url(host=host, port=port, path=path).url

    # Step 1. No path given; channel name is None
    if not path:
        return Url(host=host, port=port).url.rstrip('/'), None, scheme or None, None, None

    # Step 2. migrated_custom_channels matches
    for name, location in sorted(context.migrated_custom_channels.items(), reverse=True,
                                 key=lambda x: len(x[0])):
        location, _scheme, _auth, _token = split_scheme_auth_token(location)
        if tokenized_conda_url_startswith(test_url, join_url(location, name)):
            # translate location to new location, with new credentials
            subname = test_url.replace(join_url(location, name), '', 1).strip('/')
            channel_name = join_url(name, subname)
            channel = _get_channel_for_name(channel_name)
            return channel.location, channel_name, channel.scheme, channel.auth, channel.token

    # Step 3. migrated_channel_aliases matches
    for migrated_alias in context.migrated_channel_aliases:
        if test_url.startswith(migrated_alias.location):
            name = test_url.replace(migrated_alias.location, '', 1).strip('/')
            ca = context.channel_alias
            return ca.location, name, ca.scheme, ca.auth, ca.token

    # Step 4. custom_channels matches
    for name, channel in sorted(context.custom_channels.items(), reverse=True,
                                key=lambda x: len(x[0])):
        that_test_url = join_url(channel.location, channel.name)
        if test_url.startswith(that_test_url):
            subname = test_url.replace(that_test_url, '', 1).strip('/')
            return (channel.location, join_url(channel.name, subname), scheme,
                    channel.auth, channel.token)

    # Step 5. channel_alias match
    ca = context.channel_alias
    if ca.location and test_url.startswith(ca.location):
        name = test_url.replace(ca.location, '', 1).strip('/') or None
        return ca.location, name, scheme, ca.auth, ca.token

    # Step 6. not-otherwise-specified file://-type urls
    if host is None:
        # this should probably only happen with a file:// type url
        assert port is None
        location, name = test_url.rsplit('/', 1)
        if not location:
            location = '/'
        _scheme, _auth, _token = 'file', None, None
        return location, name, _scheme, _auth, _token

    # Step 7. fall through to host:port as channel_location and path as channel_name
    return (Url(host=host, port=port).url.rstrip('/'), path.strip('/') or None,
            scheme or None, None, None)