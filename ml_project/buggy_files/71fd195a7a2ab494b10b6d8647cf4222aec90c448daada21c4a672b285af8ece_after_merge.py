    def refresh_all_feeds(self):
        deferreds = [feed.parse_feed() for feed in self._rss_feed_dict.itervalues()]
        return DeferredList(deferreds, consumeErrors=True)