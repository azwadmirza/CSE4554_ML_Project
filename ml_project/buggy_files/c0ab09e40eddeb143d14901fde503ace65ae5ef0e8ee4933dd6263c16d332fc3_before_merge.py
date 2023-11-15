    def __init__(
        self,
        reddit: "Reddit",
        id: Optional[str] = None,  # pylint: disable=redefined-builtin
        mark_read: bool = False,
        _data: Optional[Dict[str, Any]] = None,
    ):
        """Construct an instance of the ModmailConversation object.

        :param mark_read: If True, conversation is marked as read (default: False).

        """
        super().__init__(reddit, _data=_data)
        if bool(id) == bool(_data):
            raise TypeError("Either `id` or `_data` must be provided.")

        if id:
            self.id = id

        self._info_params = {"markRead": True} if mark_read else None