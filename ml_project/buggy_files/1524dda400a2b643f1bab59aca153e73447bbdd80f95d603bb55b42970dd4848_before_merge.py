    def _parse_images(self, sid):
        """Parse images.

        This interface will be improved in future versions.
        """
        key_mapping = {'file_path': 'bannerpath', 'vote_count': 'ratingcount', 'vote_average': 'rating', 'id': 'id'}
        image_sizes = {'fanart': 'backdrop_sizes', 'poster': 'poster_sizes'}
        typecasts = {'rating': float, 'ratingcount': int}

        log.debug('Getting show banners for {0}', sid)
        _images = {}

        # Let's get the different type of images available for this series
        params = {'include_image_language': '{search_language},null'.format(search_language=self.config['language'])}

        images = self.tmdb.TV(sid).images(params=params)
        bid = images['id']
        for image_type, images in viewitems({'poster': images['posters'], 'fanart': images['backdrops']}):
            try:
                if image_type not in _images:
                    _images[image_type] = {}

                for image in images:
                    bid += 1
                    image_mapped = self._map_results(image, key_mappings=key_mapping)

                    for size in self.tmdb_configuration.images.get(image_sizes[image_type]):
                        if size == 'original':
                            width = image_mapped['width']
                            height = image_mapped['height']
                        else:
                            width = int(size[1:])
                            height = int(round(width / float(image_mapped['aspect_ratio'])))
                        resolution = '{0}x{1}'.format(width, height)

                        if resolution not in _images[image_type]:
                            _images[image_type][resolution] = {}

                        if bid not in _images[image_type][resolution]:
                            _images[image_type][resolution][bid] = {}

                        for k, v in viewitems(image_mapped):
                            if k is None or v is None:
                                continue

                            try:
                                typecast = typecasts[k]
                            except KeyError:
                                pass
                            else:
                                v = typecast(v)

                            _images[image_type][resolution][bid][k] = v
                            if k.endswith('path'):
                                new_key = '_{0}'.format(k)
                                log.debug('Adding base url for image: {0}', v)
                                _images[image_type][resolution][bid][new_key] = self.config['artwork_prefix'].format(
                                    base_url=self.tmdb_configuration.images['base_url'],
                                    image_size=size,
                                    file_path=v)

                        if size != 'original':
                            _images[image_type][resolution][bid]['rating'] = 0

            except Exception as error:
                log.warning('Could not parse Poster for show id: {0}, with exception: {1!r}', sid, error)
                return False

        season_images = self._parse_season_images(sid)
        if season_images:
            _images.update(season_images)

        self._save_images(sid, _images)
        self._set_show_data(sid, '_banners', _images)