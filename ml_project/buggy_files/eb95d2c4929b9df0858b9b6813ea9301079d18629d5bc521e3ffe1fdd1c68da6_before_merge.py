def get_locale():
    # if a user is logged in, use the locale from the user settings
    user = getattr(g, 'user', None)
    if user is not None and hasattr(user, "locale"):
        if user.nickname != 'Guest':   # if the account is the guest account bypass the config lang settings
            return user.locale
    translations = [item.language for item in babel.list_translations()] + ['en']
    preferred = [x.replace('-', '_') for x in request.accept_languages.values()]

    # In the case of Simplified Chinese, Accept-Language is "zh-CN", while our translation of Simplified Chinese is "zh_Hans_CN". 
    # TODO: This is Not a good solution, should be improved.
    if "zh_CN" in preferred:
        return "zh_Hans_CN"
    return negotiate_locale(preferred, translations)