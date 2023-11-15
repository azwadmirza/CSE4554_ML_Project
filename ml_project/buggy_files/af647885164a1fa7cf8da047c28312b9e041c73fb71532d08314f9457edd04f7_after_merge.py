def lookup_series(name=None, tvdb_id=None, only_cached=False, session=None):
    """
    Look up information on a series. Will be returned from cache if available, and looked up online and cached if not.

    Either `name` or `tvdb_id` parameter are needed to specify the series.
    :param unicode name: Name of series.
    :param int tvdb_id: TVDb ID of series.
    :param bool only_cached: If True, will not cause an online lookup. LookupError will be raised if not available
        in the cache.
    :param session: An sqlalchemy session to be used to lookup and store to cache. Commit(s) may occur when passing in
        a session. If one is not supplied it will be created.

    :return: Instance of :class:`TVDBSeries` populated with series information. If session was not supplied, this will
        be a detached from the database, so relationships cannot be loaded.
    :raises: :class:`LookupError` if series cannot be looked up.
    """
    if not (name or tvdb_id):
        raise LookupError('No criteria specified for tvdb lookup')

    log.debug('Looking up tvdb information for %s %s', name, tvdb_id)

    series = None

    def id_str():
        return '<name=%s,tvdb_id=%s>' % (name, tvdb_id)

    if tvdb_id:
        series = session.query(TVDBSeries).filter(TVDBSeries.id == tvdb_id).first()
    if not series and name:
        found = session.query(TVDBSearchResult).filter(func.lower(TVDBSearchResult.search) == name.lower()).first()
        if found and found.series:
                series = found.series
    if series:
        # Series found in cache, update if cache has expired.
        if not only_cached:
            mark_expired(session=session)
        if not only_cached and series.expired:
            log.verbose('Data for %s has expired, refreshing from tvdb', series.name)
            try:
                updated_series = TVDBSeries(id=series.id)
                series = session.merge(updated_series)
                _update_search_strings(series, search=name)
            except LookupError as e:
                log.warning('Error while updating from tvdb (%s), using cached data.', e.args[0])
        else:
            log.debug('Series %s information restored from cache.' % id_str())
    else:
        if only_cached:
            raise LookupError('Series %s not found from cache' % id_str())
        # There was no series found in the cache, do a lookup from tvdb
        log.debug('Series %s not found in cache, looking up from tvdb.', id_str())
        if tvdb_id:
            series = session.merge(TVDBSeries(id=tvdb_id))
            _update_search_strings(series, search=name)
        elif name:
            tvdb_id = find_series_id(name)
            if tvdb_id:
                series = session.query(TVDBSeries).filter(TVDBSeries.id == tvdb_id).first()
                if not series:
                    series = session.merge(TVDBSeries(tvdb_id))
                    _update_search_strings(series, search=name)

    if not series:
        raise LookupError('No results found from tvdb for %s' % id_str())
    if not series.name:
        raise LookupError('Tvdb result for series does not have a title.')

    return series