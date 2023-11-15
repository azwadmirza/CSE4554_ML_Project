    def save_data(self, filename):
        """Save profiler data."""
        self.stats1[0].dump_stats(filename)