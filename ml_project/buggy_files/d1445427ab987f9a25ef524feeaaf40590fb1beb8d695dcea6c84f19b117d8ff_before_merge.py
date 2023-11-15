    def parse(self, url, cache):
        """Parses a RSS feed. This methods supports RSS 2.0 and Media RSS.
        """
        feed = feedparser.parse(url)

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

            yield parsed_item