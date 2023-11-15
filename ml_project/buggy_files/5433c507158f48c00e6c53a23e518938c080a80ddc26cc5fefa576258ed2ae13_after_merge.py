    def __init__(self, id):
        """
        Looks up movie on tmdb and creates a new database model for it.
        These instances should only be added to a session via `session.merge`.
        """
        self.id = id
        try:
            episode = TVDBRequest().get('episodes/%s' % self.id)
        except requests.RequestException as e:
            raise LookupError('Error updating data from tvdb: %s' % e)

        self.id = episode['id']
        self.last_updated = episode['lastUpdated']
        self.season_number = episode['airedSeason']
        self.episode_number = episode['airedEpisodeNumber']
        self.absolute_number = episode['absoluteNumber']
        self.name = episode['episodeName']
        self.overview = episode['overview']
        self.director = episode['director']
        self._image = episode['filename']
        self.rating = episode['siteRating']
        self.first_aired = episode['firstAired']