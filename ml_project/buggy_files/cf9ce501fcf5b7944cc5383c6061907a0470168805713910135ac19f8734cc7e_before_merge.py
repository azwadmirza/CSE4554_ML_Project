    def __init__(self, owner, backup_storage_limit_gb):
        # The topic cache is only meant as a local lookup and should not be
        # accessed via the implemented historians.
        self._backup_cache = {}
        self._meta_data = defaultdict(dict)
        self._owner = weakref.ref(owner)
        self._backup_storage_limit_gb = backup_storage_limit_gb
        self._setupdb()