    def __init__(
        self,
        reddit: "Reddit",
        subreddit: "Subreddit",
        id: Optional[str] = None,  # pylint: disable=redefined-builtin
        reason_id: Optional[str] = None,
        _data: Optional[Dict[str, Any]] = None,
    ):
        """Construct an instance of the Removal Reason object.

        :param reddit: An instance of :class:`.Reddit`.
        :param subreddit: An instance of :class:`.Subreddit`.
        :param id: The id of the removal reason.
        :param reason_id: (Deprecated) The original name of the ``id`` parameter. Used
            for backwards compatibility. This parameter should not be used.

        """
        id = self._warn_reason_id(reason_id, id)
        if (id, _data).count(None) != 1:
            raise ValueError("Either id or _data needs to be given.")

        self.id = id
        self.subreddit = subreddit
        super().__init__(reddit, _data=_data)