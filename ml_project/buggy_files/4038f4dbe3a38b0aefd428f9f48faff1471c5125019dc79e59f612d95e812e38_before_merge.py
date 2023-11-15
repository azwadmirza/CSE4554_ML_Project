    def parse_feed(self):
        rss_parser = RSSFeedParser()

        def_list = []

        for rss_item in rss_parser.parse(self.rss_url, self._url_cache):
            if self._to_stop:
                return None

            torrent_deferred = getPage(rss_item[u'torrent_url'].encode('utf-8'))
            torrent_deferred.addCallback(lambda t, r=rss_item: self.on_got_torrent(t, rss_item=r))
            def_list.append(torrent_deferred)

        return DeferredList(def_list, consumeErrors=True)