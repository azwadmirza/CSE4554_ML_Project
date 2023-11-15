    def lookup(title=None, year=None, tmdb_id=None, imdb_id=None, smart_match=None, only_cached=False, session=None):
        """
        Do a lookup from TMDb for the movie matching the passed arguments.

        Any combination of criteria can be passed, the most specific criteria specified will be used.

        :param int tmdb_id: tmdb_id of desired movie
        :param unicode imdb_id: imdb_id of desired movie
        :param unicode title: title of desired movie
        :param int year: release year of desired movie
        :param unicode smart_match: attempt to clean and parse title and year from a string
        :param bool only_cached: if this is specified, an online lookup will not occur if the movie is not in the cache
        session: optionally specify a session to use, if specified, returned Movie will be live in that session
        :param session: sqlalchemy Session in which to do cache lookups/storage. commit may be called on a passed in
            session. If not supplied, a session will be created automatically.

        :return: The :class:`TMDBMovie` object populated with data from tmdb

        :raises: :class:`LookupError` if a match cannot be found or there are other problems with the lookup
        """
        if smart_match and not (title or tmdb_id or imdb_id):
            # If smart_match was specified, parse it into a title and year
            title_parser = get_plugin_by_name('parsing').instance.parse_movie(smart_match)
            title = title_parser.name
            year = title_parser.year
        if not (title or tmdb_id or imdb_id):
            raise LookupError('No criteria specified for TMDb lookup')
        id_str = '<title={}, year={}, tmdb_id={}, imdb_id={}>'.format(title, year, tmdb_id, imdb_id)

        log.debug('Looking up TMDb information for %s', id_str)
        movie = None
        if imdb_id or tmdb_id:
            ors = []
            if tmdb_id:
                ors.append(TMDBMovie.id == tmdb_id)
            if imdb_id:
                ors.append(TMDBMovie.imdb_id == imdb_id)
            movie = session.query(TMDBMovie).filter(or_(*ors)).first()
        elif title:
            movie_filter = session.query(TMDBMovie).filter(func.lower(TMDBMovie.name) == title.lower())
            if year:
                movie_filter = movie_filter.filter(TMDBMovie.year == year)
            movie = movie_filter.first()
            if not movie:
                search_string = title + ' ({})'.format(year) if year else ''
                found = session.query(TMDBSearchResult). \
                    filter(func.lower(TMDBSearchResult.search) == search_string.lower()).first()
                if found and found.movie:
                    movie = found.movie
        if movie:
            # Movie found in cache, check if cache has expired.
            refresh_time = timedelta(days=2)
            if movie.released:
                if movie.released > datetime.now() - timedelta(days=7):
                    # Movie is less than a week old, expire after 1 day
                    refresh_time = timedelta(days=1)
                else:
                    age_in_years = (datetime.now() - movie.released).days / 365
                    refresh_time += timedelta(days=age_in_years * 5)
            if movie.updated < datetime.now() - refresh_time and not only_cached:
                log.debug('Cache has expired for %s, attempting to refresh from TMDb.', movie.name)
                # Detach this instance from the session while we update it, then merge it back in after
                session.expunge(movie)
                try:
                    movie.update_from_tmdb()
                except LookupError:
                    log.error('Error refreshing movie details from TMDb, cached info being used.')
                else:
                    movie = session.merge(movie)
            else:
                log.debug('Movie %s information restored from cache.', movie.name)
        else:
            if only_cached:
                raise LookupError('Movie %s not found from cache' % id_str)
            # There was no movie found in the cache, do a lookup from tmdb
            log.verbose('Searching from TMDb %s', id_str)
            if imdb_id and not tmdb_id:
                try:
                    result = tmdb_request('find/{}'.format(imdb_id), external_source='imdb_id')
                except requests.RequestException as e:
                    raise LookupError('Error searching imdb id on tmdb: {}'.format(e))
                if result['movie_results']:
                    tmdb_id = result['movie_results'][0]['id']
            if not tmdb_id:
                search_string = title + ' ({})'.format(year) if year else ''
                searchparams = {'query': title}
                if year:
                    searchparams['year'] = year
                try:
                    results = tmdb_request('search/movie', **searchparams)
                except requests.RequestException as e:
                    raise LookupError('Error searching for tmdb item {}: {}'.format(search_string, e))
                if not results['results']:
                    raise LookupError('No resuts for {} from tmdb'.format(search_string))
                tmdb_id = results['results'][0]['id']
                session.add(TMDBSearchResult(search=search_string, movie_id=tmdb_id))
            if tmdb_id:
                movie = TMDBMovie(id=tmdb_id)
                movie.update_from_tmdb()
                movie = session.merge(movie)
            else:
                raise LookupError('Unable to find movie on tmdb: {}'.format(id_str))

        return movie