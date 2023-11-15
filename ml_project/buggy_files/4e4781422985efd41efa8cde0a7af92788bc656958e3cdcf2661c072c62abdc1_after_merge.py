    def request(
        self,
        method: str,
        path: str,
        params: Optional[Union[str, Dict[str, str]]] = None,
        data: Optional[
            Union[Dict[str, Union[str, Any]], bytes, IO, str]
        ] = None,
        files: Optional[Dict[str, IO]] = None,
        json=None,
    ) -> Any:
        """Return the parsed JSON data returned from a request to URL.

        :param method: The HTTP method (e.g., GET, POST, PUT, DELETE).
        :param path: The path to fetch.
        :param params: The query parameters to add to the request (default:
            None).
        :param data: Dictionary, bytes, or file-like object to send in the body
            of the request (default: None).
        :param files: Dictionary, filename to file (like) object mapping
            (default: None).
        :param json: JSON-serializable object to send in the body
            of the request with a Content-Type header of application/json
            (default: None). If ``json`` is provided, ``data`` should not be.

        """
        if data and json:
            raise ClientException(
                "At most one of `data` and `json` is supported."
            )
        try:
            return self._core.request(
                method,
                path,
                data=data,
                files=files,
                params=params,
                timeout=self.config.timeout,
                json=json,
            )
        except BadRequest as exception:
            try:
                data = exception.response.json()
            except ValueError:
                # TODO: Remove this exception after 2020-12-31 if no one has
                # filed a bug against it.
                raise Exception(
                    "Unexpected BadRequest without json body. Please file a "
                    "bug at https://github.com/praw-dev/praw/issues"
                ) from exception
            if set(data) == {"error", "message"}:
                raise
            if "fields" in data:
                assert len(data["fields"]) == 1
                field = data["fields"][0]
            else:
                field = None
            raise RedditAPIException(
                [data["reason"], data["explanation"], field]
            ) from exception