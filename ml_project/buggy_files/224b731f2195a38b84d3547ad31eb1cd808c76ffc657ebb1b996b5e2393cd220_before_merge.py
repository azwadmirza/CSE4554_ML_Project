    def validate_rss(self):
        """Validate if RSS."""
        try:
            add_cookie = self.add_cookies_from_ui()
            if not add_cookie.get('result'):
                return add_cookie

            data = self.cache._getRSSData()['entries']
            if not data:
                return {'result': False,
                        'message': 'No items found in the RSS feed {0}'.format(self.url)}

            title, url = self._get_title_and_url(data[0])

            if not title:
                return {'result': False,
                        'message': 'Unable to get title from first item'}

            if not url:
                return {'result': False,
                        'message': 'Unable to get torrent url from first item'}

            if url.startswith('magnet:') and re.search(r'urn:btih:([\w]{32,40})', url):
                return {'result': True,
                        'message': 'RSS feed Parsed correctly'}
            else:
                torrent_file = self.get_url(url, returns='content')
                try:
                    bdecode(torrent_file)
                except Exception as error:
                    self.dump_html(torrent_file)
                    return {'result': False,
                            'message': 'Torrent link is not a valid torrent file: {0}'.format(ex(error))}

            return {'result': True, 'message': 'RSS feed Parsed correctly'}

        except Exception as error:
            return {'result': False, 'message': 'Error when trying to load RSS: {0}'.format(ex(error))}