def needs_subtitles(subtitles):
    """Given the existing subtitles and wanted languages, returns True if subtitles are still needed.

    :param subtitles: the existing subtitles
    :type subtitles: set of str
    :return: True if subtitles are needed
    :rtype: bool
    """
    wanted = wanted_languages()
    if not wanted:
        return False

    if isinstance(subtitles, basestring):
        subtitles = {subtitle.strip() for subtitle in subtitles.split(',') if subtitle.strip()}

    if sickbeard.SUBTITLES_MULTI:
        return wanted.difference(subtitles)

    return 'und' not in subtitles