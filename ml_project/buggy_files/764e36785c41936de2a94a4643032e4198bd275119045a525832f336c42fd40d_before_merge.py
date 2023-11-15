    def album_for_id(self, album_id):
        """Fetches an album by its Discogs ID and returns an AlbumInfo object
        or None if the album is not found.
        """
        if not self.discogs_client:
            return

        self._log.debug(u'Searching for release {0}', album_id)
        # Discogs-IDs are simple integers. We only look for those at the end
        # of an input string as to avoid confusion with other metadata plugins.
        # An optional bracket can follow the integer, as this is how discogs
        # displays the release ID on its webpage.
        match = re.search(r'(^|\[*r|discogs\.com/.+/release/)(\d+)($|\])',
                          album_id)
        if not match:
            return None
        result = Release(self.discogs_client, {'id': int(match.group(2))})
        # Try to obtain title to verify that we indeed have a valid Release
        try:
            getattr(result, 'title')
        except DiscogsAPIError as e:
            if e.status_code != 404:
                self._log.debug(u'API Error: {0} (query: {1})', e, result._uri)
                if e.status_code == 401:
                    self.reset_auth()
                    return self.album_for_id(album_id)
            return None
        except CONNECTION_ERRORS:
            self._log.debug(u'Connection error in album lookup', exc_info=True)
            return None
        return self.get_album_info(result)