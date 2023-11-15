def refine(video, tv_episode=None, **kwargs):
    """Refine a video by using TVEpisode information.

    :param video: the video to refine.
    :type video: Episode
    :param tv_episode: the TVEpisode to be used.
    :type tv_episode: sickbeard.tv.TVEpisode
    :param kwargs:
    """
    if video.series_tvdb_id and video.tvdb_id:
        logger.debug('No need to refine with TVEpisode')
        return

    if not tv_episode:
        logger.debug('No TVEpisode to be used to refine')
        return

    if not isinstance(video, Episode):
        logger.debug('Video {name} is not an episode. Skipping refiner...', name=video.name)
        return

    if tv_episode.show:
        logger.debug('Refining using TVShow information.')
        series, year, country = series_re.match(tv_episode.show.name).groups()
        enrich({'series': series, 'year': int(year) if year else None}, video)
        enrich(SHOW_MAPPING, video, tv_episode.show)

    logger.debug('Refining using TVEpisode information.')
    enrich(EPISODE_MAPPING, video, tv_episode)
    enrich({'release_group': tv_episode.release_group}, video, overwrite=False)
    guess = Quality.to_guessit(tv_episode.status)
    enrich({'resolution': guess['screen_size'], 'format': guess['format']}, video, overwrite=False)