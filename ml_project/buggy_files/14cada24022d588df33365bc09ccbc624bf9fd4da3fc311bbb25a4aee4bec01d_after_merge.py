    def on_rss_feed_removed(self, json_result):
        if not json_result:
            return
        if json_result['removed']:
            self.load_channel_rss_feeds()