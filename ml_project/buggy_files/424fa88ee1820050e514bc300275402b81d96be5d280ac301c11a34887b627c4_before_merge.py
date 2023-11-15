    def update(self, trakt_episode, session):
        """Updates this record from the trakt media object `trakt_movie` returned by the trakt api."""
        if self.id and self.id != trakt_episode['ids']['trakt']:
            raise Exception('Tried to update db ep with different ep data')
        elif not self.id:
            self.id = trakt_episode['ids']['trakt']
        self.imdb_id = trakt_episode['ids']['imdb']
        self.tmdb_id = trakt_episode['ids']['tmdb']
        self.tvrage_id = trakt_episode['ids']['tvrage']
        if trakt_episode.get('images'):
            self.images = get_db_images(trakt_episode.get('images'), session)
        self.tvdb_id = trakt_episode['ids']['tvdb']
        self.first_aired = None
        if trakt_episode.get('first_aired'):
            self.first_aired = dateutil_parse(trakt_episode['first_aired'], ignoretz=True)
        self.updated_at = dateutil_parse(trakt_episode.get('updated_at'), ignoretz=True)
        self.cached_at = datetime.now()

        for col in ['title', 'season', 'number', 'number_abs', 'overview']:
            setattr(self, col, trakt_episode.get(col))