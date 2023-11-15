    def join(self, url: URLTypes) -> "URL":
        """
        Return an absolute URL, using given this URL as the base.
        """
        if self.is_relative_url:
            return URL(url)

        # We drop any fragment portion, because RFC 3986 strictly
        # treats URLs with a fragment portion as not being absolute URLs.
        base_uri = self._uri_reference.copy_with(fragment=None)
        relative_url = URL(url)
        return URL(relative_url._uri_reference.resolve_with(base_uri).unsplit())