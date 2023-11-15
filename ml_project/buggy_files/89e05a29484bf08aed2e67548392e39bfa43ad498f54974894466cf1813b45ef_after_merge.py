    def __init__(self, reddit: "Reddit", _data: Dict[str, Any]):
        """Construct an instance of the Message object."""
        super().__init__(reddit, _data=_data, _fetched=True)