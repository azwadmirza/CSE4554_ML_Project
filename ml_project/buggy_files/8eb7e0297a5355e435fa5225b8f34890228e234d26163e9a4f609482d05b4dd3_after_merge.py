    def playlist_uri_from_name(self, name):
        """
        Helper function to retrieve a playlist URI from its unique MPD name.
        """
        if name not in self._uri_from_name:
            self.refresh_playlists_mapping()
        return self._uri_from_name.get(name)