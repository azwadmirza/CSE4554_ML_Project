def valid_locale_fallback(desired_locale=None):
    """Provide a default fallback_locale, a string that locale.setlocale will accept.

    If desired_locale is provided must be of type str for py2x compatibility
    """
    # Whenever fallbacks change, adjust test TestHarcodedFallbacksWork
    candidates_windows = [str('English'), str('C')]
    candidates_posix = [str('en_US.utf8'), str('C')]
    candidates = candidates_windows if sys.platform == 'win32' else candidates_posix
    if desired_locale:
        candidates = list(candidates)
        candidates.insert(0, desired_locale)
    found_valid = False
    for locale_n in candidates:
        found_valid = is_valid_locale(locale_n)
        if found_valid:
            break
    if not found_valid:
        msg = 'Could not find a valid fallback locale, tried: {0}'
        utils.LOGGER.warn(msg.format(candidates))
    elif desired_locale and (desired_locale != locale_n):
        msg = 'Desired fallback locale {0} could not be set, using: {1}'
        utils.LOGGER.warn(msg.format(desired_locale, locale_n))
    return locale_n