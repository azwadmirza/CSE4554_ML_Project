def guess_locale_from_lang_posix(lang):
    """Guess a locale, basing on POSIX system language."""
    # compatibility v6.0.4
    if is_valid_locale(str(lang)):
        locale_n = str(lang)
    else:
        # this works in Travis when locale support set by Travis suggestion
        locale_n = str((locale.normalize(lang).split('.')[0]) + '.UTF-8')
    if not is_valid_locale(locale_n):
        # http://thread.gmane.org/gmane.comp.web.nikola/337/focus=343
        locale_n = str((locale.normalize(lang).split('.')[0]))
    if not is_valid_locale(locale_n):
        locale_n = None
    return locale_n