    def stats(self):
        """
        Returns
            dict?: resource stats
        """
        stats = self.get("stats")
        if stats is None:
            stats = {"hash": "", "bytes": 0}
            if self.tabular:
                stats.update({"fields": 0, "rows": 0})
            stats = self.metadata_attach("stats", stats)
        return stats