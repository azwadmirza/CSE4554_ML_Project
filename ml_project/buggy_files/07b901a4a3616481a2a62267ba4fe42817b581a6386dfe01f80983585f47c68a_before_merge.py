    def _get_show_by_id(self, tvmaze_id, request_language='en'):  # pylint: disable=unused-argument
        """
        Retrieve tvmaze show information by tvmaze id, or if no tvmaze id provided by passed external id.

        :param tvmaze_id: The shows tvmaze id
        :return: An ordered dict with the show searched for.
        """
        results = None
        if tvmaze_id:
            logger.debug('Getting all show data for %s', [tvmaze_id])
            results = self.tvmaze_api.get_show(maze_id=tvmaze_id)

        if not results:
            return

        mapped_results = self._map_results(results, self.series_map)

        return OrderedDict({'series': mapped_results})