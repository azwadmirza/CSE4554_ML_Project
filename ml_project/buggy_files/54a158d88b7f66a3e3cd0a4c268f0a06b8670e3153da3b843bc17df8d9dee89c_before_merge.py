    def host(self) -> str:
        """
        The URL host as a string.
        Always normlized to lowercase, and IDNA encoded.

        Examples:

        url = httpx.URL("http://www.EXAMPLE.org")
        assert url.host == "www.example.org"

        url = httpx.URL("http://中国.icom.museum")
        assert url.host == "xn--fiqs8s.icom.museum"
        """
        return self._uri_reference.host or ""