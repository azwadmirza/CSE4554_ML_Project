    def _create_recommended_show(self, show_obj):
        """Create the RecommendedShow object from the returned showobj."""
        rec_show = RecommendedShow(self,
                                   show_obj['show']['ids'], show_obj['show']['title'],
                                   INDEXER_TVDBV2,  # indexer
                                   show_obj['show']['ids']['tvdb'],
                                   **{'rating': show_obj['show']['rating'],
                                      'votes': try_int(show_obj['show']['votes'], '0'),
                                      'image_href': 'http://www.trakt.tv/shows/{0}'.format(show_obj['show']['ids']['slug']),
                                      # Adds like: {'tmdb': 62126, 'tvdb': 304219, 'trakt': 79382, 'imdb': 'tt3322314',
                                      # 'tvrage': None, 'slug': 'marvel-s-luke-cage'}
                                      'ids': show_obj['show']['ids']
                                      }
                                   )

        use_default = None
        image = None
        try:
            image = tvdb_api_v2.series_id_images_query_get(show_obj['show']['ids']['tvdb'], key_type='poster').data[0].file_name
        except Exception:
            use_default = self.default_img_src
            logger.log('Missing poster on TheTVDB for show %s' % (show_obj['show']['title']), logger.DEBUG)

        rec_show.cache_image('http://thetvdb.com/banners/{0}'.format(image), default=use_default)
        # As the method below requires allot of resources, i've only enabled it when
        # the shows language or country is 'jp' (japanese). Looks a litle bit akward,
        # but alternative is allot of resource used
        if 'jp' in [show_obj['show']['country'], show_obj['show']['language']]:
            rec_show.check_if_anime(self.anidb, show_obj['show']['ids']['tvdb'])

        return rec_show