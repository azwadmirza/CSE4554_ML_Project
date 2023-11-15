    def __init__(
        self, url: typing.Union["URL", str, RawURL] = "", params: QueryParamTypes = None
    ) -> None:
        if isinstance(url, (str, tuple)):
            if isinstance(url, tuple):
                raw_scheme, raw_host, port, raw_path = url
                scheme = raw_scheme.decode("ascii")
                host = raw_host.decode("ascii")
                port_str = "" if port is None else f":{port}"
                path = raw_path.decode("ascii")
                url = f"{scheme}://{host}{port_str}{path}"

            try:
                self._uri_reference = rfc3986.iri_reference(url).encode()
            except rfc3986.exceptions.InvalidAuthority as exc:
                raise InvalidURL(message=str(exc)) from None

            if self.is_absolute_url:
                # We don't want to normalize relative URLs, since doing so
                # removes any leading `../` portion.
                self._uri_reference = self._uri_reference.normalize()
        elif isinstance(url, URL):
            self._uri_reference = url._uri_reference
        else:
            raise TypeError(
                f"Invalid type for url.  Expected str or httpx.URL, got {type(url)}"
            )

        # Add any query parameters, merging with any in the URL if needed.
        if params:
            if self._uri_reference.query:
                url_params = QueryParams(self._uri_reference.query)
                url_params.update(params)
                query_string = str(url_params)
            else:
                query_string = str(QueryParams(params))
            self._uri_reference = self._uri_reference.copy_with(query=query_string)