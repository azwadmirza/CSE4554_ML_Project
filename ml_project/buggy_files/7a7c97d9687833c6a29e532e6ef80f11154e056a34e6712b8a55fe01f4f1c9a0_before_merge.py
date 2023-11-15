def wanted_languages():
    """Returns the wanted language codes

    :return: set of wanted subtitles (opensubtitles codes)
    :rtype: frozenset
    """
    return frozenset(sickbeard.SUBTITLES_LANGUAGES).intersection(subtitle_code_filter())