def _update_settings(option):
    """Update global settings when qwebsettings changed."""
    global_settings.update_setting(option)

    if option in ['scrolling.bar', 'content.user_stylesheets']:
        _init_stylesheet(default_profile)
        _init_stylesheet(private_profile)
        _update_stylesheet()
    elif option in ['content.headers.user_agent',
                    'content.headers.accept_language']:
        _set_http_headers(default_profile)
        _set_http_headers(private_profile)
    elif option == 'content.cache.size':
        _set_http_cache_size(default_profile)
        _set_http_cache_size(private_profile)
    elif (option == 'content.cookies.store' and
          # https://bugreports.qt.io/browse/QTBUG-58650
          qtutils.version_check('5.9', compiled=False)):
        _set_persistent_cookie_policy(default_profile)
        # We're not touching the private profile's cookie policy.
    elif option == 'spellcheck.languages':
        _set_dictionary_language(default_profile)
        _set_dictionary_language(private_profile, warn=False)