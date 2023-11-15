    def __init__(self, *args, **kwargs):  # pylint: disable=too-many-locals,too-many-arguments
        """Tmdb api constructor."""
        super(Tmdb, self).__init__(*args, **kwargs)

        self.tmdb = tmdb
        self.tmdb.API_KEY = TMDB_API_KEY
        self.tmdb.REQUESTS_SESSION = self.config['session']
        self.tmdb_configuration = self.tmdb.Configuration()
        try:
            self.response = self.tmdb_configuration.info()
        except RequestException as e:
            raise IndexerUnavailable('Indexer TMDB is unavailable at this time. Cause: {cause}'.format(cause=e))

        self.config['artwork_prefix'] = '{base_url}{image_size}{file_path}'

        # An api to indexer series/episode object mapping
        self.series_map = {
            'id': 'id',
            'name': 'seriesname',
            'original_name': 'aliasnames',
            'overview': 'overview',
            'air_date': 'firstaired',
            'first_air_date': 'firstaired',
            'backdrop_path': 'fanart',
            'url': 'show_url',
            'episode_number': 'episodenumber',
            'season_number': 'seasonnumber',
            'dvd_episode_number': 'dvd_episodenumber',
            'last_air_date': 'airs_dayofweek',
            'last_updated': 'lastupdated',
            'network_id': 'networkid',
            'vote_average': 'contentrating',
            'poster_path': 'poster',
            'genres': 'genre',
            'type': 'classification',
            'networks': 'network',
            'episode_run_time': 'runtime'
        }

        self.episodes_map = {
            'id': 'id',
            'name': 'episodename',
            'overview': 'overview',
            'air_date': 'firstaired',
            'episode_run_time': 'runtime',
            'episode_number': 'episodenumber',
            'season_number': 'seasonnumber',
            'vote_average': 'contentrating',
            'still_path': 'filename'
        }