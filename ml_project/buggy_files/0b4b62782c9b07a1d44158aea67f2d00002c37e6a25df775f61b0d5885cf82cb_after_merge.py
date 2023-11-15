def _init_profiles():
    """Init the two used QWebEngineProfiles."""
    global default_profile, private_profile

    default_profile = QWebEngineProfile.defaultProfile()
    default_profile.setter = ProfileSetter(default_profile)
    default_profile.setCachePath(
        os.path.join(standarddir.cache(), 'webengine'))
    default_profile.setPersistentStoragePath(
        os.path.join(standarddir.data(), 'webengine'))
    default_profile.setter.init_profile()
    default_profile.setter.set_persistent_cookie_policy()

    private_profile = QWebEngineProfile()
    private_profile.setter = ProfileSetter(private_profile)
    assert private_profile.isOffTheRecord()
    private_profile.setter.init_profile()