    def external_ids(self, **kwargs):
        """
        Get the external ids that we have stored for a TV season by season
        number.

        Args:
            language: (optional) ISO 639 code.

        Returns:
            A dict respresentation of the JSON returned from the API.
        """
        path = self._get_series_id_season_number_path('external_ids')

        response = self._GET(path, kwargs)
        self._set_attrs_to_values(response)
        return response