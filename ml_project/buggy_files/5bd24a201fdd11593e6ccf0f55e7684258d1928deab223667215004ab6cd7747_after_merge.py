    def get(self, name, method):
        """
        Retrieve a StatsEntry instance by name and method
        """
        entry = self.entries.get((name, method))
        if not entry:
            entry = StatsEntry(self, name, method, use_response_times_cache=self.use_response_times_cache)
            self.entries[(name, method)] = entry
        return entry