    def stats(self):
        """
        Returns
            dict?: resource stats
        """
        stats = {"hash": "", "bytes": 0, "fields": 0, "rows": 0}
        return self.metadata_attach("stats", self.get("stats", stats))