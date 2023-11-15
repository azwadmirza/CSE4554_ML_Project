    def url_rewrite(self, task, entry):
        series_url = entry['url']
        search_title = re.sub('\[.*\] ', '', entry['title'])

        self.config = task.config.get('serienjunkies') or {}
        self.config.setdefault('hoster', DEFAULT_HOSTER)
        self.config.setdefault('language', DEFAULT_LANGUAGE)

        download_urls = self.parse_downloads(series_url, search_title)
        if not download_urls:
            entry.reject('No Episode found')
        else:
            entry['url'] = download_urls[-1]
            entry['description'] = ", ".join(download_urls)

        # Debug Information
        log.debug('TV Show URL: %s', series_url)
        log.debug('Episode: %s', search_title)
        log.debug('Download URL: %s', download_urls)