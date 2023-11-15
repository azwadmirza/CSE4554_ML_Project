def get_video(video_path, subtitles_dir=None, subtitles=True, embedded_subtitles=None, release_name=None):
    """Returns the subliminal video for the given path

    :param video_path: the video path
    :type video_path: str
    :param subtitles_dir: the subtitles directory
    :type subtitles_dir: str
    :param subtitles: True if existing external subtitles should be taken into account
    :type subtitles: bool
    :param embedded_subtitles: True if embedded subtitles should be taken into account
    :type embedded_subtitles: bool
    :param release_name: the release name
    :type release_name: str
    :return: video
    :rtype: subliminal.video
    """
    return _get_video(video_path, subtitles_dir, subtitles, embedded_subtitles, release_name)