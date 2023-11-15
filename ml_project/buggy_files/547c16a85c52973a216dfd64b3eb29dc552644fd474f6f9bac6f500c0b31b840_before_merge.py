def get_subtitles(video):
    """Returns a sorted list of detected subtitles for the given video file.

    :param video: the video to be inspected
    :type video: subliminal.video.Video
    :return: sorted list of opensubtitles code for the given video
    :rtype: list of str
    """
    result_list = [l.opensubtitles for l in video.subtitle_languages if hasattr(l, 'opensubtitles') and l.opensubtitles]
    return sorted(result_list)