    def set_indexer_data(self, season=None, indexer_api=None):
        """Set episode information from indexer.

        :param season:
        :param indexer_api:
        :rtype: bool
        """
        if season is None:
            season = self.season

        if indexer_api is None or indexer_api.indexer != self.series.indexer_api.indexer:
            api = self.series.indexer_api
        else:
            api = indexer_api

        try:
            api._get_episodes(self.series.series_id, aired_season=season)
        except IndexerError as error:
            log.warning(
                '{id}: {indexer} threw up an error: {error_msg}', {
                    'id': self.series.series_id,
                    'indexer': indexerApi(self.indexer).name,
                    'error_msg': ex(error),
                }
            )
            return False

        return True