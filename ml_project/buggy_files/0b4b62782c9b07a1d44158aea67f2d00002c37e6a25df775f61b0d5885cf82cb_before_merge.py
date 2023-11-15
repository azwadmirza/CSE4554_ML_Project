def _init_profiles():
    """Init the two used QWebEngineProfiles."""
    global default_profile, private_profile

    default_profile = QWebEngineProfile.defaultProfile()
    default_profile.setCachePath(
        os.path.join(standarddir.cache(), 'webengine'))
    default_profile.setPersistentStoragePath(
        os.path.join(standarddir.data(), 'webengine'))
    _init_profile(default_profile)
    _set_persistent_cookie_policy(default_profile)

    private_profile = QWebEngineProfile()
    assert private_profile.isOffTheRecord()
    _init_profile(private_profile)