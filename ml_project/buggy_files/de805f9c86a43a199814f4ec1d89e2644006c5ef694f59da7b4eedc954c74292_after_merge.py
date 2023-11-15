def run_subs_extra_scripts(video_path, subtitle_path, subtitle_language, show_name, season, episode, episode_name,
                           show_indexerid):
    """Execute the subtitles extra-scripts for the given video path.

    :param video_path: the video path
    :type video_path: str
    :param subtitle_path: the downloaded subtitle path
    :type subtitle_path: str
    :param subtitle_language: the subtitle language
    :type subtitle_language: babelfish.Language
    :param show_name: the show name
    :type show_name: str
    :param season: the episode season number
    :type season: int
    :param episode: the episode number
    :type episode: int
    :param episode_name: the episode name
    :type episode_name: str
    :param show_indexerid: the show indexer id
    :type show_indexerid: int
    """
    run_subs_scripts(video_path, sickbeard.SUBTITLES_EXTRA_SCRIPTS, video_path, subtitle_path,
                     subtitle_language.opensubtitles, show_name, season, episode, episode_name, show_indexerid)