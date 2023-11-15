    def lookup_movie(session=None, only_cached=None, **lookup_params):
        movie = get_cached('movie', session=session, **lookup_params)
        title = lookup_params.get('title') or ''
        found = None
        if not movie and title:
            found = session.query(TraktMovieSearchResult).filter(TraktMovieSearchResult.search == title.lower()).first()
            if found and found.movie:
                log.debug('Found %s in previous search results as %s', title, found.movie.title)
                movie = found.movie
        if only_cached:
            if movie:
                return movie
            raise LookupError('Movie %s not found from cache' % lookup_params)
        if movie and not movie.expired:
            return movie
        try:
            trakt_movie = get_trakt('movie', **lookup_params)
        except LookupError as e:
            if movie:
                log.debug('Error refreshing movie data from trakt, using cached. %s', e)
                return movie
            raise
        movie = session.query(TraktMovie).filter(TraktMovie.id == trakt_movie['ids']['trakt']).first()
        if movie:
            movie.update(trakt_movie, session)
        else:
            movie = TraktMovie(trakt_movie, session)
            session.add(movie)
        if movie and title.lower() == movie.title.lower():
            return movie
        if movie and title and not found:
            if not session.query(TraktMovieSearchResult).filter(TraktMovieSearchResult.search == title.lower()).first():
                log.debug('Adding search result to db')
                session.add(TraktMovieSearchResult(search=title, movie=movie))
        elif movie and found:
            log.debug('Updating search result in db')
            found.movie = movie
        return movie