    def update(self, trakt_movie, session):
        """Updates this record from the trakt media object `trakt_movie` returned by the trakt api."""
        if self.id and self.id != trakt_movie['ids']['trakt']:
            raise Exception('Tried to update db movie with different movie data')
        elif not self.id:
            self.id = trakt_movie['ids']['trakt']
        self.slug = trakt_movie['ids']['slug']
        self.imdb_id = trakt_movie['ids']['imdb']
        self.tmdb_id = trakt_movie['ids']['tmdb']
        for col in ['title', 'overview', 'runtime', 'rating', 'votes',
                    'language', 'tagline', 'year', 'trailer', 'homepage']:
            setattr(self, col, trakt_movie.get(col))
        if trakt_movie.get('released'):
            self.released = dateutil_parse(trakt_movie.get('released'), ignoretz=True)
        self.updated_at = dateutil_parse(trakt_movie.get('updated_at'), ignoretz=True)
        self.genres[:] = get_db_genres(trakt_movie.get('genres', []), session)
        self.translations[:] = get_db_trans(trakt_movie.get('available_translations', []), session)
        self.cached_at = datetime.now()
        self.images = get_db_images(trakt_movie.get('images'), session)