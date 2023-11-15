    def host(self) -> str:
        """
        The URL host as a string.
        Always normlized to lowercase, and IDNA encoded.

        Examples:

        url = httpx.URL("http://www.EXAMPLE.org")
        assert url.host == "www.example.org"

        url = httpx.URL("http://中国.icom.museum")
        assert url.host == "xn--fiqs8s.icom.museum"

        url = httpx.URL("https://[::ffff:192.168.0.1]")
        assert url.host == "::ffff:192.168.0.1"
        """
        host: str = self._uri_reference.host

        if host and ":" in host and host[0] == "[":
            # it's an IPv6 address
            host = host.lstrip("[").rstrip("]")

        return host or ""