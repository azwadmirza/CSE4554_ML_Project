    def get_albums(self, query):
        """Returns a list of AlbumInfo objects for a discogs search query.
        """
        # Strip non-word characters from query. Things like "!" and "-" can
        # cause a query to return no results, even if they match the artist or
        # album title. Use `re.UNICODE` flag to avoid stripping non-english
        # word characters.
        # FIXME: Encode as ASCII to work around a bug:
        # https://github.com/beetbox/beets/issues/1051
        # When the library is fixed, we should encode as UTF-8.
        query = re.sub(r'(?u)\W+', ' ', query).encode('ascii', "replace")
        # Strip medium information from query, Things like "CD1" and "disk 1"
        # can also negate an otherwise positive result.
        query = re.sub(br'(?i)\b(CD|disc)\s*\d+', b'', query)
        try:
            releases = self.discogs_client.search(query,
                                                  type='release').page(1)
        except CONNECTION_ERRORS:
            self._log.debug(u"Communication error while searching for {0!r}",
                            query, exc_info=True)
            return []
        return [album for album in map(self.get_album_info, releases[:5])
                if album]