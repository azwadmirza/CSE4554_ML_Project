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
        data = data or {}
        try:
            return self._objectify_request(
                data=data,
                files=files,
                method="POST",
                params=params,
                path=path,
            )
        except RedditAPIException as exception:
            seconds = self._handle_rate_limit(exception=exception)
            if seconds is not None:
                logger.debug(
                    "Rate limit hit, sleeping for {:.2f} seconds".format(
                        seconds
                    )
                )
                time.sleep(seconds)
                return self._objectify_request(
                    data=data,
                    files=files,
                    method="POST",
                    params=params,
                    path=path,
                )
            raise