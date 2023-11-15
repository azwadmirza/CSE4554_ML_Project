    def keywords(self, **kwargs):
        """
        Get the plot keywords for a specific movie id.
        
        Args:
            append_to_response: (optional) Comma separated, any movie method.

        Returns:
            A dict respresentation of the JSON returned from the API.
        """
        path = self._get_id_path('keywords')

        response = self._GET(path, kwargs)
        self._set_attrs_to_values(response)
        return response