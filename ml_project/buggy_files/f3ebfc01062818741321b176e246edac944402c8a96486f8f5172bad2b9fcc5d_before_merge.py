    def __init__(
        self,
        reddit: "Reddit",
        thread_id: Optional[str] = None,
        update_id: Optional[str] = None,
        _data: Optional[Dict[str, Any]] = None,
    ):
        """Initialize a lazy :class:`.LiveUpdate` instance.

        Either ``thread_id`` and ``update_id``, or ``_data`` must be provided.

        :param reddit: An instance of :class:`.Reddit`.
        :param thread_id: A live thread ID, e.g., ``"ukaeu1ik4sw5"``.
        :param update_id: A live update ID, e.g.,
            ``"7827987a-c998-11e4-a0b9-22000b6a88d2"``.

        Usage:

        .. code-block:: python

            update = LiveUpdate(reddit, "ukaeu1ik4sw5", "7827987a-c998-11e4-a0b9-22000b6a88d2")
            update.thread  # LiveThread(id="ukaeu1ik4sw5")
            update.id  # "7827987a-c998-11e4-a0b9-22000b6a88d2"
            update.author  # "umbrae"

        """
        if _data is not None:
            # Since _data (part of JSON returned from reddit) have no thread ID,
            # self._thread must be set by the caller of LiveUpdate(). See the code of
            # LiveThread.updates() for example.
            super().__init__(reddit, _data=_data)
            self._fetched = True
        elif thread_id and update_id:
            super().__init__(reddit, _data=None)
            self._thread = LiveThread(self._reddit, thread_id)
            self.id = update_id
        else:
            raise TypeError(
                "Either `thread_id` and `update_id`, or `_data` must be provided."
            )