    def patch(
        self,
        path: str,
        data: Optional[
            Union[Dict[str, Union[str, Any]], bytes, IO, str]
        ] = None,
    ) -> Any:
        """Return parsed objects returned from a PATCH request to ``path``.

        :param path: The path to fetch.
        :param data: Dictionary, bytes, or file-like object to send in the body
            of the request (default: None).

        """
        data = self.request("PATCH", path, data=data)
        return self._objector.objectify(data)