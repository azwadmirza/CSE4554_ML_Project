    def on_rss_feed_added(self, json_result):
        if not json_result:
            return
        if json_result['added']:
            self.load_channel_rss_feeds()