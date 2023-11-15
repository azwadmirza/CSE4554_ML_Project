def is_profile_configured(opts, provider, profile_name):
    '''
    Check if the requested profile contains the minimum required parameters for
    a profile.

    Required parameters include image, provider, and size keys.

    .. versionadded:: Beryllium
    '''
    required_keys = ['image', 'provider', 'size']
    alias, driver = provider.split(':')
    provider_key = opts['providers'][alias][driver]
    profile_key = opts['providers'][alias][driver]['profiles'][profile_name]

    # Check if image and/or size are supplied in the provider config. If either
    # one is present, remove it from the required_keys list.
    for item in required_keys:
        if item in provider_key:
            required_keys.remove(item)

    # Check for remaining required parameters in the profile config.
    for item in required_keys:
        if profile_key.get(item, None) is None:
            # There's at least one required configuration item which is not set.
            log.error(
                'The required {0!r} configuration setting is missing from the '
                '{1!r} profile, which is configured '
                'under the {2!r} alias.'.format(
                    item, profile_name, alias
                )
            )
            return False

    return True