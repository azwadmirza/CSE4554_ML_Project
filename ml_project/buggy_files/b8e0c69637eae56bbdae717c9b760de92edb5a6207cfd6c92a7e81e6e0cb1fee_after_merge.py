def _update_settings(option):
    """Update global settings when qwebsettings changed."""
    global_settings.update_setting(option)

    if option in ['content.headers.user_agent',
                  'content.headers.accept_language']:
        default_profile.setter.set_http_headers()
        private_profile.setter.set_http_headers()
    elif option == 'content.cache.size':
        default_profile.setter.set_http_cache_size()
        private_profile.setter.set_http_cache_size()
    elif (option == 'content.cookies.store' and
          # https://bugreports.qt.io/browse/QTBUG-58650
          qtutils.version_check('5.9', compiled=False)):
        default_profile.setter.set_persistent_cookie_policy()
        # We're not touching the private profile's cookie policy.
    elif option == 'spellcheck.languages':
        default_profile.setter.set_dictionary_language()
        private_profile.setter.set_dictionary_language(warn=False)