    def keywords(self):
        """
        Get the plot keywords for a specific movie id.

        Returns:
            A dict respresentation of the JSON returned from the API.
        """
        path = self._get_id_path('keywords')

        response = self._GET(path)
        self._set_attrs_to_values(response)
        return response