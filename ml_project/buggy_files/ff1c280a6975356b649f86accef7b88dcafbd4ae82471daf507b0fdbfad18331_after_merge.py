    def _get_rss_data(self):
        """Get RSS data."""
        return self.get_rss_feed(self.provider.url)