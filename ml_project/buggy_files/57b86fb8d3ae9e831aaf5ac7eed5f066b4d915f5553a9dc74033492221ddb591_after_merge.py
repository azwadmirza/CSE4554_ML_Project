def merge_subtitles(existing_subtitles, new_subtitles):
    """Merge the existing and new subtitles to a single list.

    Consolidates the existing_subtitles and the new_subtitles into a resulting list without repetitions. If
    SUBTITLES_MULTI is disabled and there's only one new subtitle, an `und` element is added to the returning list
    instead of using the new_subtitles.

    :param existing_subtitles: list: opensubtitles codes of the existing subtitles
    :type existing_subtitles: list of str
    :param new_subtitles: list: opensubtitles codes of the new subtitles
    :type new_subtitles: list of str
    :return: list of opensubtitles codes of the resulting subtitles
    :rtype: list of str
    """
    current_subtitles = sorted(
        {subtitle for subtitle in new_subtitles + existing_subtitles}) if existing_subtitles else new_subtitles

    if not sickbeard.SUBTITLES_MULTI and len(new_subtitles) == 1:
        current_subtitles.remove(new_subtitles[0])
        current_subtitles.append('und')

    return current_subtitles