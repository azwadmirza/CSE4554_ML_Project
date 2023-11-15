def download_subtitles(video_path, show_name, season, episode, episode_name, show_indexerid, release_name, status,
                       existing_subtitles):  # pylint: disable=too-many-locals, too-many-branches, too-many-statements
    """Downloads missing subtitles for the given episode

    Checks whether subtitles are needed or not

    :param video_path: the video path
    :type video_path: str
    :param show_name: the show name
    :type show_name: str
    :param season: the season number
    :type season: int
    :param episode: the episode number
    :type episode: int
    :param episode_name: the episode name
    :type episode_name: str
    :param show_indexerid: the show indexerid
    :type show_indexerid: int
    :param release_name: the release name
    :type release_name: str
    :param status: the show status
    :type status: int
    :param existing_subtitles: list of existing subtitles (opensubtitles codes)
    :type existing_subtitles: list of str
    :return: a sorted list of the opensubtitles codes for the downloaded subtitles
    :rtype: list of str
    """
    ep_num = episode_num(season, episode) or episode_num(season, episode, numbering='absolute')
    languages = get_needed_languages(existing_subtitles)

    if not languages:
        logger.debug(u'Episode already has all needed subtitles, skipping %s %s', show_name, ep_num)
        return []

    logger.debug(u'Checking subtitle candidates for %s %s (%s)', show_name, ep_num, os.path.basename(video_path))

    subtitles_dir = get_subtitles_dir(video_path)
    found_subtitles = download_best_subs(video_path, subtitles_dir, release_name, languages)

    for subtitle in found_subtitles:
        if sickbeard.SUBTITLES_EXTRA_SCRIPTS and isMediaFile(video_path):
            subtitle_path = compute_subtitle_path(subtitle, video_path, subtitles_dir)
            run_subs_extra_scripts(video_path=video_path, subtitle_path=subtitle_path,
                                   subtitle_language=subtitle.language, show_name=show_name, season=season,
                                   episode=episode, episode_name=episode_name, show_indexerid=show_indexerid)
        if sickbeard.SUBTITLES_HISTORY:
            logger.debug(u'history.logSubtitle %s, %s', subtitle.provider_name, subtitle.language.opensubtitles)
            history.logSubtitle(show_indexerid, season, episode, status, subtitle)

    return sorted({subtitle.language.opensubtitles for subtitle in found_subtitles})