    def candidates(self, items, artist, album, va_likely):
        """Returns a list of AlbumInfo objects for discogs search results
        matching an album and artist (if not various).
        """
        if not self.discogs_client:
            return

        if va_likely:
            query = album
        else:
            query = '%s %s' % (artist, album)
        try:
            return self.get_albums(query)
        except DiscogsAPIError as e:
            self._log.debug(u'API Error: {0} (query: {1})', e, query)
            return []
        except (ConnectionError, socket.error) as e:
            self._log.debug(u'HTTP Connection Error: {0}', e)
            return []