def compute_subtitle_path(subtitle, video_path, subtitles_dir):
    """Returns the full subtitle path that's computed by subliminal

    :param subtitle: the subtitle
    :type subtitle: subliminal.Subtitle
    :param video_path: the video path
    :type video_path: str
    :param subtitles_dir: the subtitles directory
    :type subtitles_dir: str
    :return: the computed subtitles path
    :rtype: str
    """
    subtitle_path = get_subtitle_path(video_path, subtitle.language if sickbeard.SUBTITLES_MULTI else None)
    return os.path.join(subtitles_dir, os.path.split(subtitle_path)[1]) if subtitles_dir else subtitle_path