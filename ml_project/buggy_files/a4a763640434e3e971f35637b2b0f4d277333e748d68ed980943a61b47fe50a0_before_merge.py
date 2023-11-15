    def _get_query(self):
        if self.is_local:
            return self.track.to_string()
        elif self.is_spotify:
            return self.spotify_uri
        elif self.is_search and self.is_youtube:
            return f"ytsearch:{self.track}"
        elif self.is_search and self.is_soundcloud:
            return f"scsearch:{self.track}"
        return self.track