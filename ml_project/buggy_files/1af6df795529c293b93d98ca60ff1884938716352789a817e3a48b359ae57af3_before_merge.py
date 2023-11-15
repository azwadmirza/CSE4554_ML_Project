    def post(
        self,
        path: str,
        data: Optional[
            Union[Dict[str, Union[str, Any]], bytes, IO, str]
        ] = None,
        files: Optional[Dict[str, IO]] = None,
        params: Optional[Union[str, Dict[str, str]]] = None,
    ) -> Any:
        """Return parsed objects returned from a POST request to ``path``.

        :param path: The path to fetch.
        :param data: Dictionary, bytes, or file-like object to send in the body
            of the request (default: None).
        :param files: Dictionary, filename to file (like) object mapping
            (default: None).
        :param params: The query parameters to add to the request (default:
            None).

        """
        data = self.request(
            "POST", path, data=data or {}, files=files, params=params
        )
        return self._objector.objectify(data)