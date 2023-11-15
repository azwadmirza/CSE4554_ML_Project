    def __init__(self, use_response_times_cache=True):
        """
        The value of use_response_times_cache will be set for each StatsEntry() when they are created.
        Settings it to False saves some memory and CPU cycles which we can do on worker nodes where 
        the response_times_cache is not needed.
        """
        self.use_response_times_cache = use_response_times_cache
        self.entries = {}
        self.errors = {}
        self.total = StatsEntry(self, "Aggregated", None, use_response_times_cache=self.use_response_times_cache)