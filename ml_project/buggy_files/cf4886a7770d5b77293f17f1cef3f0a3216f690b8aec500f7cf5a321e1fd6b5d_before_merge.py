    def __init__(self,
                 name: str,
                 description: str = "",
                 tag_keys: Optional[Tuple[str]] = None):
        if len(name) == 0:
            raise ValueError("Empty name is not allowed. "
                             "Please provide a metric name.")
        self._name = name
        self._description = description
        # We don't specify unit because it won't be
        # exported to Prometheus anyway.
        self._unit = ""
        # The default tags key-value pair.
        self._default_tags = {}
        # Keys of tags.
        self._tag_keys = tag_keys or tuple()
        # The Cython metric class. This should be set in the child class.
        self._metric = None

        if not isinstance(self._tag_keys, tuple):
            raise ValueError("tag_keys should be a tuple type, got: "
                             f"{type(self._tag_keys)}")