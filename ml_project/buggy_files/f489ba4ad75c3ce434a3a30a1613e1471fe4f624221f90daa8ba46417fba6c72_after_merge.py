    def __init__(
        self,
        reddit: "Reddit",
        id: Optional[str] = None,  # pylint: disable=redefined-builtin
        url: Optional[str] = None,
        _data: Optional[Dict[str, Any]] = None,
    ):
        """Initialize a Submission instance.

        :param reddit: An instance of :class:`~.Reddit`.
        :param id: A reddit base36 submission ID, e.g., ``2gmzqe``.
        :param url: A URL supported by :meth:`~praw.models.Submission.id_from_url`.

        Either ``id`` or ``url`` can be provided, but not both.

        """
        if (id, url, _data).count(None) != 2:
            raise TypeError("Exactly one of `id`, `url`, or `_data` must be provided.")
        self.comment_limit = 2048

        # Specify the sort order for ``comments``
        self.comment_sort = "confidence"

        if id:
            self.id = id
        elif url:
            self.id = self.id_from_url(url)

        super().__init__(reddit, _data=_data)

        self._comments_by_id = {}