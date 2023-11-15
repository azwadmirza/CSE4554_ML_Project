    def __init__(self, reddit: "Reddit", _data: Optional[Dict[str, Any]]):
        """Initialize a RedditBase instance (or a subclass).

        :param reddit: An instance of :class:`~.Reddit`.

        """
        super().__init__(reddit, _data=_data)
        self._fetched = False