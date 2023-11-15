    def _create_recommended_show(self, series, storage_key=None):
        """Create the RecommendedShow object from the returned showobj."""
        rec_show = RecommendedShow(
            self,
            series['show']['ids'], series['show']['title'],
            INDEXER_TVDBV2,  # indexer
            series['show']['ids']['tvdb'],
            **{'rating': series['show']['rating'],
                'votes': try_int(series['show']['votes'], '0'),
                'image_href': 'http://www.trakt.tv/shows/{0}'.format(series['show']['ids']['slug']),
                # Adds like: {'tmdb': 62126, 'tvdb': 304219, 'trakt': 79382, 'imdb': 'tt3322314',
                # 'tvrage': None, 'slug': 'marvel-s-luke-cage'}
                'ids': series['show']['ids']
               }
        )

        use_default = None
        image = None
        try:
            if not missing_posters.has(series['show']['ids']['tvdb']):
                image = self.check_cache_for_poster(series['show']['ids']['tvdb']) or \
                    self.tvdb_api_v2.config['session'].series_api.series_id_images_query_get(
                        series['show']['ids']['tvdb'], key_type='poster').data[0].file_name
            else:
                log.info('CACHE: Missing poster on TVDB for show {0}', series['show']['title'])
                use_default = self.default_img_src
        except ApiException as error:
            use_default = self.default_img_src
            if getattr(error, 'status', None) == 404:
                log.info('Missing poster on TheTVDB for show {0}', series['show']['title'])
                missing_posters.append(series['show']['ids']['tvdb'])
        except Exception as error:
            use_default = self.default_img_src
            log.debug('Missing poster on TheTVDB, cause: {0!r}', error)

        image_url = ''
        if image:
            image_url = self.tvdb_api_v2.config['artwork_prefix'].format(image=image)

        rec_show.cache_image(image_url, default=use_default)

        # As the method below requires a lot of resources, i've only enabled it when
        # the shows language or country is 'jp' (japanese). Looks a litle bit akward,
        # but alternative is a lot of resource used
        if 'jp' in [series['show']['country'], series['show']['language']]:
            rec_show.flag_as_anime(series['show']['ids']['tvdb'])

        return rec_show