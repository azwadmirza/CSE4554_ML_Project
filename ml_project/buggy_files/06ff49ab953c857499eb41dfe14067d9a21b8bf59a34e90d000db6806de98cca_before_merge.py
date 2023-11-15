    def clear_all(self):
        """
        Remove all stats entries and errors
        """
        self.total = StatsEntry(self, "Aggregated", None, use_response_times_cache=True)
        self.entries = {}
        self.errors = {}