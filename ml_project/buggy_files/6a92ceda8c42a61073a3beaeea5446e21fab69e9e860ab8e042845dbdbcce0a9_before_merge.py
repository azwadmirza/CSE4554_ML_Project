    def fetch_popular_shows(self):
        """Get popular show information from IMDB."""
        popular_shows = []

        imdb_result = self.imdb_api.get_popular_shows()

        for imdb_show in imdb_result['ranks']:
            series = {}
            imdb_id = series['imdb_tt'] = imdb_show['id'].strip('/').split('/')[-1]

            if imdb_id:
                show_details = cached_get_imdb_series_details(imdb_id)
                if show_details:
                    try:
                        series['year'] = imdb_show.get('year')
                        series['name'] = imdb_show['title']
                        series['image_url_large'] = imdb_show['image']['url']
                        series['image_path'] = posixpath.join('images', 'imdb_popular',
                                                              os.path.basename(series['image_url_large']))
                        series['image_url'] = '{0}{1}'.format(imdb_show['image']['url'].split('V1')[0], '_SY600_AL_.jpg')
                        series['imdb_url'] = 'http://www.imdb.com{imdb_id}'.format(imdb_id=imdb_show['id'])
                        series['votes'] = show_details['ratings'].get('ratingCount', 0)
                        series['outline'] = show_details['plot'].get('outline', {}).get('text')
                        series['rating'] = show_details['ratings'].get('rating', 0)
                    except Exception as error:
                        log.warning('Could not parse show {imdb_id} with error: {error!r}',
                                    {'imdb_id': imdb_id, 'error': error})
                else:
                    continue

            if all([series['year'], series['name'], series['imdb_tt']]):
                popular_shows.append(series)

        result = []
        for series in popular_shows:
            try:
                recommended_show = self._create_recommended_show(series, storage_key='imdb_{0}'.format(series['imdb_tt']))
                if recommended_show:
                    result.append(recommended_show)
            except RequestException:
                log.warning(
                    u'Could not connect to indexers to check if you already have'
                    u' this show in your library: {show} ({year})',
                    {'show': series['name'], 'year': series['name']}
                )

        # Update the dogpile index. This will allow us to retrieve all stored dogpile shows from the dbm.
        update_recommended_series_cache_index('imdb', [binary_type(s.series_id) for s in result])

        return result