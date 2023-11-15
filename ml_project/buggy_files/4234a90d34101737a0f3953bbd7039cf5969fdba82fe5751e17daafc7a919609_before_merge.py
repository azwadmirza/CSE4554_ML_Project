    def lookup_series(session=None, only_cached=None, **lookup_params):
        series = get_cached('show', session=session, **lookup_params)
        title = lookup_params.get('title') or ''
        found = None
        if not series and title:
            found = session.query(TraktShowSearchResult).filter(TraktShowSearchResult.search == title.lower()).first()
            if found and found.series:
                log.debug('Found %s in previous search results as %s', title, found.series.title)
                series = found.series
        if only_cached:
            if series:
                return series
            raise LookupError('Series %s not found from cache' % lookup_params)
        if series and not series.expired:
            return series
        try:
            trakt_show = get_trakt('show', **lookup_params)
        except LookupError as e:
            if series:
                log.debug('Error refreshing show data from trakt, using cached. %s', e)
                return series
            raise
        series = session.query(TraktShow).filter(TraktShow.id == trakt_show['ids']['trakt']).first()
        if series:
            series.update(trakt_show, session)
        else:
            series = TraktShow(trakt_show, session)
            session.add(series)
        if series and title.lower() == series.title.lower():
            return series
        elif series and title and not found:
            if not session.query(TraktShowSearchResult).filter(TraktShowSearchResult.search == title.lower()).first():
                log.debug('Adding search result to db')
                session.add(TraktShowSearchResult(search=title, series=series))
        elif series and found:
            log.debug('Updating search result in db')
            found.series = series
        return series