    def _get(self, endpoint):  # type: (str) -> Union[dict, None]
        try:
            json_response = self._session.get(self._url + endpoint)
        except TooManyRedirects:
            # Cache control redirect loop.
            # We try to remove the cache and try again
            self._cache_control_cache.delete(self._url + endpoint)
            json_response = self._session.get(self._url + endpoint)

        if json_response.status_code == 404:
            return None

        json_data = json_response.json()

        return json_data