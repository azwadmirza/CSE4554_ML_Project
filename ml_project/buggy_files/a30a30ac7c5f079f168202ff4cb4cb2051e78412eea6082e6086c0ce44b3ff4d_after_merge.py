    def __init__(
        self,
        reddit: "Reddit",
        id: Optional[str] = None,
        _data: Optional[Dict[str, Any]] = None,  # pylint: disable=redefined-builtin
    ):
        """Initialize a lazy :class:`.LiveThread` instance.

        :param reddit: An instance of :class:`.Reddit`.
        :param id: A live thread ID, e.g., ``"ukaeu1ik4sw5"``

        """
        if (id, _data).count(None) != 1:
            raise TypeError("Either `id` or `_data` must be provided.")
        if id:
            self.id = id
        super().__init__(reddit, _data=_data)