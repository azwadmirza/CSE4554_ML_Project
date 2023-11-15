def get_locale():
    # if a user is logged in, use the locale from the user settings
    user = getattr(g, 'user', None)
    if user is not None and hasattr(user, "locale"):
        if user.nickname != 'Guest':   # if the account is the guest account bypass the config lang settings
            return user.locale
    translations = [str(item) for item in babel.list_translations()] + ['en']
    preferred = list()
    for x in request.accept_languages.values():
        try:
            preferred.append(str(LC.parse(x.replace('-', '_'))))
        except (UnknownLocaleError, ValueError) as e:
            app.logger.debug("Could not parse locale: %s", e)
            preferred.append('en')
    return negotiate_locale(preferred, translations)