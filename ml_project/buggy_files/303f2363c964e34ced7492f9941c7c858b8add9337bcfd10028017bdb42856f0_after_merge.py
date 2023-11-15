    def get(
        self, path: str, params: Optional[Union[str, Dict[str, str]]] = None
    ):
        """Return parsed objects returned from a GET request to ``path``.

        :param path: The path to fetch.
        :param params: The query parameters to add to the request (default:
            None).

        """
        return self._objectify_request(method="GET", params=params, path=path)