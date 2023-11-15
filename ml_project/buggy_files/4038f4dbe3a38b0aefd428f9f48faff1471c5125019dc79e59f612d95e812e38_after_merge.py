    def parse_feed(self):
        rss_parser = RSSFeedParser()

        def on_rss_items(rss_items):
            def_list = []
            for rss_item in rss_items:
                if self._to_stop:
                    continue

                torrent_url = rss_item[u'torrent_url'].encode('utf-8')
                if torrent_url.startswith('magnet:'):
                    self._logger.warning(u"Tribler does not support adding magnet links to a channel from a RSS feed.")
                    continue

                torrent_deferred = getPage(torrent_url)
                torrent_deferred.addCallbacks(lambda t, r=rss_item: self.on_got_torrent(t, rss_item=r),
                                              self.on_got_torrent_error)
                def_list.append(torrent_deferred)

            return DeferredList(def_list, consumeErrors=True)

        return rss_parser.parse(self.rss_url, self._url_cache).addCallback(on_rss_items)