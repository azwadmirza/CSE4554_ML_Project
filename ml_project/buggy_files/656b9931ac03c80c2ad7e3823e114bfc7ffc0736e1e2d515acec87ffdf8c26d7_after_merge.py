def get_current_subtitles(video_path):
    """Returns a list of current subtitles for the episode

    :param video_path: the video path
    :type video_path: str
    :return: the current subtitles (3-letter opensubtitles codes) for the specified video
    :rtype: list of str
    """
    video = get_video(video_path)
    if not video:
        logger.log(u"Exception caught in subliminal.scan_video, subtitles couldn't be refreshed", logger.DEBUG)
    else:
        return get_subtitles(video)