    def _parse_season_images(self, tvmaze_id):
        """Parse Show and Season posters."""
        seasons = {}
        if tvmaze_id:
            logger.debug('Getting all show data for %s', tvmaze_id)
            try:
                seasons = self.tvmaze_api.show_seasons(maze_id=tvmaze_id)
            except BaseError as e:
                logger.warning('Getting show seasons for the season images failed. Cause: %s', e)

        _images = {'season': {'original': {}}}
        # Get the season posters
        for season in seasons.keys():
            if not getattr(seasons[season], 'image', None):
                continue
            if season not in _images['season']['original']:
                _images['season']['original'][season] = {seasons[season].id: {}}
            _images['season']['original'][season][seasons[season].id]['_bannerpath'] = seasons[season].image['original']
            _images['season']['original'][season][seasons[season].id]['rating'] = 1

        return _images