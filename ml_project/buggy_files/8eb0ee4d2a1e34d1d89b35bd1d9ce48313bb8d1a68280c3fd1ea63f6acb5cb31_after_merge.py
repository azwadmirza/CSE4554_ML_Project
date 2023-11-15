    def __init__(
        self,
        reddit: "Reddit",
        id: Optional[str] = None,  # pylint: disable=redefined-builtin
        url: Optional[str] = None,
        _data: Optional[Dict[str, Any]] = None,
    ):
        """Construct an instance of the Comment object."""
        if (id, url, _data).count(None) != 2:
            raise TypeError("Exactly one of `id`, `url`, or `_data` must be provided.")
        fetched = False
        self._replies = []
        self._submission = None
        if id:
            self.id = id
        elif url:
            self.id = self.id_from_url(url)
        else:
            fetched = True
        super().__init__(reddit, _data=_data, _fetched=fetched)