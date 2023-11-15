    def _parse_images(self, tvmaze_id):
        """Parse Show and Season posters.

        images are retrieved using t['show name]['_banners'], for example:

        >>> t = TVMaze(images = True)
        >>> t['scrubs']['_banners'].keys()
        ['fanart', 'poster', 'series', 'season']
        >>> t['scrubs']['_banners']['poster']['680x1000']['35308']['_bannerpath']
        u'http://theTMDB.com/banners/posters/76156-2.jpg'
        >>>

        Any key starting with an underscore has been processed (not the raw
        data from the XML)

        This interface will be improved in future versions.
        """
        logger.debug('Getting show banners for %s', tvmaze_id)

        try:
            image_medium = self.shows[tvmaze_id]['image_medium']
        except Exception:
            logger.debug('Could not parse Poster for showid: %s', tvmaze_id)
            return False

        # Set the poster (using the original uploaded poster for now, as the medium formated is 210x195
        _images = {u'poster': {u'1014x1500': {u'1': {u'rating': 1,
                                                     u'language': u'en',
                                                     u'ratingcount': 1,
                                                     u'bannerpath': image_medium.split('/')[-1],
                                                     u'bannertype': u'poster',
                                                     u'bannertype2': u'210x195',
                                                     u'_bannerpath': image_medium,
                                                     u'id': u'1035106'}}}}

        season_images = self._parse_season_images(tvmaze_id)
        if season_images:
            _images.update(season_images)

        self._save_images(tvmaze_id, _images)
        self._set_show_data(tvmaze_id, '_banners', _images)