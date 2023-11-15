    def __init__(self, query: Union[LocalPath, str], **kwargs):
        query = kwargs.get("queryforced", query)
        self._raw: Union[LocalPath, str] = query

        _localtrack: LocalPath = LocalPath(query)

        self.track: Union[LocalPath, str] = _localtrack if (
            (_localtrack.is_file() or _localtrack.is_dir()) and _localtrack.exists()
        ) else query

        self.valid: bool = query != "InvalidQueryPlaceHolderName"
        self.is_local: bool = kwargs.get("local", False)
        self.is_spotify: bool = kwargs.get("spotify", False)
        self.is_youtube: bool = kwargs.get("youtube", False)
        self.is_soundcloud: bool = kwargs.get("soundcloud", False)
        self.is_bandcamp: bool = kwargs.get("bandcamp", False)
        self.is_vimeo: bool = kwargs.get("vimeo", False)
        self.is_mixer: bool = kwargs.get("mixer", False)
        self.is_twitch: bool = kwargs.get("twitch", False)
        self.is_other: bool = kwargs.get("other", False)
        self.is_playlist: bool = kwargs.get("playlist", False)
        self.is_album: bool = kwargs.get("album", False)
        self.is_search: bool = kwargs.get("search", False)
        self.is_stream: bool = kwargs.get("stream", False)
        self.single_track: bool = kwargs.get("single", False)
        self.id: Optional[str] = kwargs.get("id", None)
        self.invoked_from: Optional[str] = kwargs.get("invoked_from", None)
        self.local_name: Optional[str] = kwargs.get("name", None)
        self.search_subfolders: bool = kwargs.get("search_subfolders", False)
        self.spotify_uri: Optional[str] = kwargs.get("uri", None)

        self.start_time: int = kwargs.get("start_time", 0)
        self.track_index: Optional[int] = kwargs.get("track_index", None)

        if self.invoked_from == "sc search":
            self.is_youtube = False
            self.is_soundcloud = True

        self.lavalink_query: str = self._get_query()

        if self.is_playlist or self.is_album:
            self.single_track = False