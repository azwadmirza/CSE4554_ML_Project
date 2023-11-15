def subtitle_code_filter():
    """Return a set of all 3-letter code languages of opensubtitles.

    :return: all 3-letter language codes
    :rtype: set of str
    """
    return {code for code in language_converters['opensubtitles'].codes if len(code) == 3}