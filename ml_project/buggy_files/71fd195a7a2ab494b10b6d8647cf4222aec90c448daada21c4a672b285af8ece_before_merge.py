    def refresh_all_feeds(self):
        [feed.parse_feed() for feed in self._rss_feed_dict.itervalues()]