def get_needed_languages(subtitles):
    """Given the existing subtitles, returns a set of the needed subtitles.

    :param subtitles: the existing subtitles (opensubtitles codes)
    :type subtitles: list of str
    :return: the needed subtitles
    :rtype: set of babelfish.Language
    """
    if not sickbeard.SUBTITLES_MULTI:
        return set() if 'und' in subtitles else {from_code(language) for language in wanted_languages()}
    return {from_code(language) for language in wanted_languages().difference(subtitles)}