    def clear_all(self):
        """
        Remove all stats entries and errors
        """
        self.total = StatsEntry(self, "Aggregated", None, use_response_times_cache=self.use_response_times_cache)
        self.entries = {}
        self.errors = {}