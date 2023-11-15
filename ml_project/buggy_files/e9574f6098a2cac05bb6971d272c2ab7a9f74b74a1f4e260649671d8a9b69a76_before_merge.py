def get_subtitle_description(subtitle):
    """Returns a human readable name/description for the given subtitle (if possible)

    :param subtitle: the given subtitle
    :type subtitle: subliminal.Subtitle
    :return: name/description
    :rtype: str
    """
    desc = None
    if hasattr(subtitle, 'filename') and subtitle.filename:
        desc = subtitle.filename.lower()
    elif hasattr(subtitle, 'name') and subtitle.name:
        desc = subtitle.name.lower()
    if hasattr(subtitle, 'release') and subtitle.release:
        desc = subtitle.release.lower()
    if hasattr(subtitle, 'releases') and subtitle.releases:
        desc = str(subtitle.releases).lower()

    if not desc:
        desc = subtitle.id

    return subtitle.id + '-' + desc if desc not in subtitle.id else desc