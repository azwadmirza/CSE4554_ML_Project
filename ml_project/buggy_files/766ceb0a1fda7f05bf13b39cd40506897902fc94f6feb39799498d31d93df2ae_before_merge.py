    def videos(self, **kwargs):
        """
        Get the videos that have been added to a TV season (trailers, teasers,
        etc...).

        Args:
            language: (optional) ISO 639 code.

        Returns:
            A dict respresentation of the JSON returned from the API.
        """
        path = self._get_id_season_number_path('videos')

        response = self._GET(path, kwargs)
        self._set_attrs_to_values(response)
        return response