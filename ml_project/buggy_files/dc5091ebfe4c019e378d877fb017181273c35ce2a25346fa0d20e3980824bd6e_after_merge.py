    def validateRSS(self):

        try:
            if self.cookies:
                success, status = self.add_cookies_from_ui()
                if not success:
                    return False, status

            # Access to a protected member of a client class
            data = self.cache._get_rss_data()['entries']
            if not data:
                return False, 'No items found in the RSS feed {0}'.format(self.url)

            title, url = self._get_title_and_url(data[0])

            if not title:
                return False, 'Unable to get title from first item'

            if not url:
                return False, 'Unable to get torrent url from first item'

            if url.startswith('magnet:') and re.search(r'urn:btih:([\w]{32,40})', url):
                return True, 'RSS feed Parsed correctly'
            else:
                torrent_file = self.get_url(url, returns='content')
                try:
                    bencodepy.decode(torrent_file)
                except (bencodepy.exceptions.BencodeDecodeError, Exception) as error:
                    self.dumpHTML(torrent_file)
                    return False, 'Torrent link is not a valid torrent file: {0}'.format(error)

            return True, 'RSS feed Parsed correctly'

        except Exception as error:
            return False, 'Error when trying to load RSS: {0}'.format(str(error))