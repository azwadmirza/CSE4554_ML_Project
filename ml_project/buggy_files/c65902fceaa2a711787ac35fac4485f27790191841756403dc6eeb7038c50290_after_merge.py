    def __init__(self, obj):
        """Initialize handler."""
        self.obj = obj
        self._objid = obj.id
        self._model = to_str(obj.__dbclass__.__name__.lower())
        self._cache = {}
        # store category names fully cached
        self._catcache = {}
        # full cache was run on all attributes
        self._cache_complete = False