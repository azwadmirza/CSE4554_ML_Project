def get_current_subtitles(video_path):
    """Returns a list of current subtitles for the episode

    :param video_path: the video path
    :return: the current subtitles for the specified video
    """
    video = get_video(video_path)
    if not video:
        logger.log(u"Exception caught in subliminal.scan_video, subtitles couldn't be refreshed", logger.DEBUG)
    else:
        return get_subtitles(video)