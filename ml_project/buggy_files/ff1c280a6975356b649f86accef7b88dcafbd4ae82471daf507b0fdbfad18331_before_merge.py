    def _get_rss_data(self):
        """Get RSS data."""
        self.provider.add_cookies_from_ui()
        return self.get_rss_feed(self.provider.url)