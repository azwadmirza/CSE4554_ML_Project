    def __init__(
        self,
        reddit: "Reddit",
        _data: Optional[Dict[str, Any]],
        _extra_attribute_to_check: Optional[str] = None,
        _fetched: bool = False,
        _str_field: bool = True,
    ):
        """Initialize a RedditBase instance (or a subclass).

        :param reddit: An instance of :class:`~.Reddit`.

        """
        super().__init__(reddit, _data=_data)
        self._fetched = _fetched
        if _str_field and self.STR_FIELD not in self.__dict__:
            if (
                _extra_attribute_to_check is not None
                and _extra_attribute_to_check in self.__dict__
            ):
                return
            raise ValueError(
                f"An invalid value was specified for {self.STR_FIELD}. Check that the "
                f"argument for the {self.STR_FIELD} parameter is not empty."
            )