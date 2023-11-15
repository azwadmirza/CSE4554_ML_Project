    def parse(self, url, cache):
        """
        Parses a RSS feed. This methods supports RSS 2.0 and Media RSS.
        """
        def on_rss_response(response):
            feed = feedparser.parse(response)
            feed_items = []

            for item in feed.entries:
                # ignore the ones that we have seen before
                link = item.get(u'link', None)
                if link is None or cache.has(link):
                    continue

                title = self._html2plaintext(item[u'title']).strip()
                description = self._html2plaintext(item.get(u'media_description', u'')).strip()
                torrent_url = item[u'link']

                thumbnail_list = []
                media_thumbnail_list = item.get(u'media_thumbnail', None)
                if media_thumbnail_list:
                    for thumbnail in media_thumbnail_list:
                        thumbnail_list.append(thumbnail[u'url'])

                # assemble the information
                parsed_item = {u'title': title,
                               u'description': description,
                               u'torrent_url': torrent_url,
                               u'thumbnail_list': thumbnail_list}

                feed_items.append(parsed_item)

            return feed_items

        def on_rss_error(failure):
            self._logger.error("Error when fetching RSS feed: %s", failure)

        return http_get(str(url)).addCallbacks(on_rss_response, on_rss_error)