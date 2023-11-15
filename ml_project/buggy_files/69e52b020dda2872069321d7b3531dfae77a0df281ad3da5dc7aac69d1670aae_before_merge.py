    def put(
        self,
        path: str,
        data: Optional[
            Union[Dict[str, Union[str, Any]], bytes, IO, str]
        ] = None,
    ):
        """Return parsed objects returned from a PUT request to ``path``.

        :param path: The path to fetch.
        :param data: Dictionary, bytes, or file-like object to send in the body
            of the request (default: None).

        """
        data = self.request("PUT", path, data=data)
        return self._objector.objectify(data)