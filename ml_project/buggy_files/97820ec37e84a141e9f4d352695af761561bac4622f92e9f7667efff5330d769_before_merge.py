def lookup_episode(name=None, season_number=None, episode_number=None, absolute_number=None,
                   tvdb_id=None, only_cached=False, session=None):
    """
    Look up information on an episode. Will be returned from cache if available, and looked up online and cached if not.

    Either `name` or `tvdb_id` parameter are needed to specify the series.
    Either `seasonnum` and `episodedum`, `absolutenum`, or `airdate` are required to specify episode number.
    :param unicode name: Name of series episode belongs to.
    :param int tvdb_id: TVDb ID of series episode belongs to.
    :param int season_number: Season number of episode.
    :param int episode_number: Episode number of episode.
    :param int absolute_number: Absolute number of episode.
    :param bool only_cached: If True, will not cause an online lookup. LookupError will be raised if not available
        in the cache.
    :param session: An sqlalchemy session to be used to lookup and store to cache. Commit(s) may occur when passing in
        a session. If one is not supplied it will be created, however if you need to access relationships you should
        pass one in.

    :return: Instance of :class:`TVDBEpisode` populated with series information.
    :raises: :class:`LookupError` if episode cannot be looked up.
    """
    # First make sure we have the series data
    series = lookup_series(name=name, tvdb_id=tvdb_id, only_cached=only_cached, session=session)

    if not series:
        LookupError('Series %s (%s) not found from' % (name, tvdb_id))

    ep_description = series.name
    query_params = {}
    episode = session.query(TVDBEpisode).filter(TVDBEpisode.series_id == series.id)

    if absolute_number:
        episode = episode.filter(TVDBEpisode.absolute_number == absolute_number)
        query_params['absoluteNumber'] = absolute_number
        ep_description = '%s absNo: %s' % (ep_description, absolute_number)

    if season_number:
        episode = episode.filter(TVDBEpisode.season_number == season_number)
        query_params['airedSeason'] = season_number
        ep_description = '%s s%s' % (ep_description, season_number)

    if episode_number:
        episode = episode.filter(TVDBEpisode.episode_number == episode_number)
        query_params['airedEpisode'] = episode_number
        ep_description = '%s e%s' % (ep_description, episode_number)

    episode = episode.first()

    if episode:
        if episode.expired and not only_cached:
            log.info('Data for %r has expired, refreshing from tvdb', episode)
            try:
                episode.update()
            except LookupError as e:
                log.warning('Error while updating from tvdb (%s), using cached data.' % str(e))
        else:
            log.debug('Using episode info for %s from cache.', ep_description)
    else:
        if only_cached:
            raise LookupError('Episode %s not found from cache' % ep_description)
        # There was no episode found in the cache, do a lookup from tvdb
        log.debug('Episode %s not found in cache, looking up from tvdb.', ep_description)
        try:
            results = TVDBRequest().get('series/%s/episodes/query' % series.id, **query_params)
            if results:
                # Check if this episode id is already in our db
                episode = session.query(TVDBEpisode).filter(TVDBEpisode.id == results[0]['id']).first()
                if not episode:
                    episode = TVDBEpisode(id=results[0]['id'])
                if episode.expired is not False:
                    episode.update()

                series.episodes.append(episode)
                session.merge(series)
        except requests.RequestException as e:
            raise LookupError('Error looking up episode from TVDb (%s)' % e)
    if episode:
        return episode
    else:
        raise LookupError('No results found for %s' % ep_description)