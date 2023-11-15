    def _create_recommended_show(self, series, storage_key=None):
        """Create the RecommendedShow object from the returned showobj."""
        tvdb_id = helpers.get_tvdb_from_id(series.get('imdb_tt'), 'IMDB')

        if not tvdb_id:
            return None

        rec_show = RecommendedShow(
            self,
            series.get('imdb_tt'),
            series.get('name'),
            INDEXER_TVDBV2,
            int(tvdb_id),
            **{'rating': series.get('rating'),
               'votes': series.get('votes'),
               'image_href': series.get('imdb_url')}
        )

        if series.get('image_url'):
            rec_show.cache_image(series.get('image_url'))

        return rec_show