def get_subtitle_description(subtitle):
    """Return a human readable name/description for the given subtitle (if possible).

    :param subtitle: the given subtitle
    :type subtitle: subliminal.Subtitle
    :return: name/description
    :rtype: str
    """
    desc = None
    sub_id = unicode(subtitle.id)
    if hasattr(subtitle, 'filename') and subtitle.filename:
        desc = subtitle.filename.lower()
    elif hasattr(subtitle, 'name') and subtitle.name:
        desc = subtitle.name.lower()
    if hasattr(subtitle, 'release') and subtitle.release:
        desc = subtitle.release.lower()
    if hasattr(subtitle, 'releases') and subtitle.releases:
        desc = unicode(subtitle.releases).lower()

    if not desc:
        desc = sub_id

    return sub_id + '-' + desc if desc not in sub_id else desc