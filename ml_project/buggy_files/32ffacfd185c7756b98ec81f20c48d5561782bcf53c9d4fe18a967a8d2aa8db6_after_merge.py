    def __init__(
        self,
        reddit: "Reddit",
        name: Optional[str] = None,
        fullname: Optional[str] = None,
        _data: Optional[Dict[str, Any]] = None,
    ):
        """Initialize a Redditor instance.

        :param reddit: An instance of :class:`~.Reddit`.
        :param name: The name of the redditor.
        :param fullname: The fullname of the redditor, starting with ``t2_``.

        Exactly one of ``name``, ``fullname`` or ``_data`` must be provided.

        """
        if (name, fullname, _data).count(None) != 2:
            raise TypeError(
                "Exactly one of `name`, `fullname`, or `_data` must be provided."
            )
        if _data:
            assert (
                isinstance(_data, dict) and "name" in _data
            ), "Please file a bug with PRAW"
        self._listing_use_sort = True
        if name:
            self.name = name
        elif fullname:
            self._fullname = fullname
        super().__init__(reddit, _data=_data, _extra_attribute_to_check="_fullname")