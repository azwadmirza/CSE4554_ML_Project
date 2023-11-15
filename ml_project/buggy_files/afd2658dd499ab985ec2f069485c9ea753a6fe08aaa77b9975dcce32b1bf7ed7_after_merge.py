    def _spotify_format_call(qtype: str, key: str) -> Tuple[str, MutableMapping]:
        params = {}
        if qtype == "album":
            query = f"https://api.spotify.com/v1/albums/{key}/tracks"
        elif qtype == "track":
            query = f"https://api.spotify.com/v1/tracks/{key}"
        else:
            query = f"https://api.spotify.com/v1/playlists/{key}/tracks"
        return query, params