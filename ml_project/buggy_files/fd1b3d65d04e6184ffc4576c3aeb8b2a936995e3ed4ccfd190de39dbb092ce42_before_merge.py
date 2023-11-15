    def info(self, **kwargs):
        """
        Get the primary information about a TV season by its season number.

        Args:
            language: (optional) ISO 639 code.
            append_to_response: (optional) Comma separated, any TV series
                                method.

        Returns:
            A dict respresentation of the JSON returned from the API.
        """
        path = self._get_id_season_number_path('info')

        response = self._GET(path, kwargs)
        self._set_attrs_to_values(response)
        return response