def get_subtitles_dir(video_path):
    """Return the correct subtitles directory based on the user configuration.

    If the directory doesn't exist, it will be created

    :param video_path: the video path
    :type video_path: str
    :return: the subtitles directory
    :rtype: str
    """
    if not sickbeard.SUBTITLES_DIR:
        return os.path.dirname(video_path)

    if os.path.isabs(sickbeard.SUBTITLES_DIR):
        return _decode(sickbeard.SUBTITLES_DIR)

    new_subtitles_path = os.path.join(os.path.dirname(video_path), sickbeard.SUBTITLES_DIR)
    if sickbeard.helpers.makeDir(new_subtitles_path):
        sickbeard.helpers.chmodAsParent(new_subtitles_path)
    else:
        logger.warning(u'Unable to create subtitles folder %s', new_subtitles_path)

    return new_subtitles_path