def run_subs_pre_scripts(video_path):
    """Executes the subtitles pre-scripts for the given video path

    :param video_path: the video path
    :type video_path: str
    """
    run_subs_scripts(video_path, sickbeard.SUBTITLES_PRE_SCRIPTS, [video_path])