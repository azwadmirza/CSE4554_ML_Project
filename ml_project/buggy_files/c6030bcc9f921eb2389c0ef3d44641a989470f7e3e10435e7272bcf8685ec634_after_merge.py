    def __init__(self, tvdb_id):
        """
        Looks up movie on tvdb and creates a new database model for it.
        These instances should only be added to a session via `session.merge`.
        """
        self.id = tvdb_id

        try:
            series = TVDBRequest().get('series/%s' % self.id)
        except requests.RequestException as e:
            raise LookupError('Error updating data from tvdb: %s' % e)

        self.id = series['id']
        self.language = 'en'
        self.last_updated = series['lastUpdated']
        self.name = series['seriesName']
        self.rating = float(series['siteRating']) if series['siteRating'] else 0.0
        self.status = series['status']
        self.runtime = int(series['runtime']) if series['runtime'] else 0
        self.airs_time = series['airsTime']
        self.airs_dayofweek = series['airsDayOfWeek']
        self.content_rating = series['rating']
        self.network = series['network']
        self.overview = series['overview']
        self.imdb_id = series['imdbId']
        self.zap2it_id = series['zap2itId']
        self.first_aired = series['firstAired']
        self.expired = False
        self.aliases = series['aliases']
        self._banner = series['banner']
        self._genres = [TVDBGenre(id=name) for name in series['genre']] if series['genre'] else []

        # Actors and Posters are lazy populated
        self._actors = None
        self._posters = None