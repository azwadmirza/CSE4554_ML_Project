    def __init__(
        self,
        reddit: "Reddit",
        _data: Dict[str, Any] = None,
        collection_id: Optional[str] = None,
        permalink: Optional[str] = None,
    ):
        """Initialize this collection.

        :param reddit: An instance of :class:`.Reddit`.
        :param _data: Any data associated with the Collection (optional).
        :param collection_id: The ID of the Collection (optional).
        :param permalink: The permalink of the Collection (optional).
        """
        if (_data, collection_id, permalink).count(None) != 2:
            raise TypeError(
                "Exactly one of _data, collection_id, or permalink must be provided."
            )

        if permalink:
            collection_id = self._url_parts(permalink)[4]

        if collection_id:
            self.collection_id = collection_id  # set from _data otherwise

        super().__init__(reddit, _data)

        self._info_params = {
            "collection_id": self.collection_id,
            "include_links": True,
        }