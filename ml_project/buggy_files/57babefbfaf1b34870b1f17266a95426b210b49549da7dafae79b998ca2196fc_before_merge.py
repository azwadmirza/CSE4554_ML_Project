def get_current_subtitles(video_path):
    """Returns a list of current subtitles for the episode.

    :param video_path: the video path
    :type video_path: str
    :return: the current subtitles (3-letter opensubtitles codes) for the specified video
    :rtype: list of str
    """
    # invalidate the cached video entry for the given path
    invalidate_video_cache(video_path)

    # get the latest video information
    video = get_video(video_path)
    if not video:
        logger.info(u"Exception caught in subliminal.scan_video, subtitles couldn't be refreshed for %s", video_path)
    else:
        return get_subtitles(video)