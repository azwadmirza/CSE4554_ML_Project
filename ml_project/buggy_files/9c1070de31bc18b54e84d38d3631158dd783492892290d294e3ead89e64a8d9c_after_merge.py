    def initialize_with_rss_feeds(self, rss_feeds):
        if not rss_feeds:
            return
        self.window().edit_channel_rss_feeds_list.clear()
        for feed in rss_feeds["rssfeeds"]:
            item = QTreeWidgetItem(self.window().edit_channel_rss_feeds_list)
            item.setText(0, feed["url"])

            self.window().edit_channel_rss_feeds_list.addTopLevelItem(item)