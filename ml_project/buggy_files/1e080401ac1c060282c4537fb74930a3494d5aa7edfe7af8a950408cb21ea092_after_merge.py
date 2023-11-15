    def update(self, trakt_show, session):
        """Updates this record from the trakt media object `trakt_show` returned by the trakt api."""
        if self.id and self.id != trakt_show['ids']['trakt']:
            raise Exception('Tried to update db show with different show data')
        elif not self.id:
            self.id = trakt_show['ids']['trakt']
        self.slug = trakt_show['ids']['slug']
        self.imdb_id = trakt_show['ids']['imdb']
        self.tmdb_id = trakt_show['ids']['tmdb']
        self.tvrage_id = trakt_show['ids']['tvrage']
        self.tvdb_id = trakt_show['ids']['tvdb']
        if trakt_show.get('images'):
            set_image_attributes(self, trakt_show)
        if trakt_show.get('airs'):
            airs = trakt_show.get('airs')
            self.air_day = airs.get('day')
            self.timezone = airs.get('timezone')
            if airs.get('time'):
                self.air_time = datetime.strptime(airs.get('time'), '%H:%M').time()
            else:
                self.air_time = None
        if trakt_show.get('first_aired'):
            self.first_aired = dateutil_parse(trakt_show.get('first_aired'), ignoretz=True)
        else:
            self.first_aired = None
        self.updated_at = dateutil_parse(trakt_show.get('updated_at'), ignoretz=True)

        for col in ['overview', 'runtime', 'rating', 'votes', 'language', 'title', 'year',
                    'runtime', 'certification', 'network', 'country', 'status', 'aired_episodes',
                    'trailer', 'homepage']:
            setattr(self, col, trakt_show.get(col))

        self.genres = [TraktGenre(name=g.replace(' ', '-')) for g in trakt_show.get('genres', [])]
        self.cached_at = datetime.now()
        self.translation_languages = trakt_show.get('available_translations', [])