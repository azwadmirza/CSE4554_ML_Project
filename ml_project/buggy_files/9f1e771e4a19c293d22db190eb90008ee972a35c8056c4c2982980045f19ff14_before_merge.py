    def scrape(self, bestmatch=True, tries_remaining=5):
        """ Search and scrape YouTube to return a list of matching videos. """

        # prevents an infinite loop but allows for a few retries
        if tries_remaining == 0:
            log.debug('No tries left. I quit.')
            return

        search_url = generate_search_url(self.search_query)
        log.debug('Opening URL: {0}'.format(search_url))

        item = urllib.request.urlopen(search_url).read()
        items_parse = BeautifulSoup(item, "html.parser")

        videos = []
        for x in items_parse.find_all('div', {'class': 'yt-lockup-dismissable yt-uix-tile'}):

            if not is_video(x):
                continue

            y = x.find('div', class_='yt-lockup-content')
            link = y.find('a')['href'][-11:]
            title = y.find('a')['title']

            try:
                videotime = x.find('span', class_="video-time").get_text()
            except AttributeError:
                log.debug('Could not find video duration on YouTube, retrying..')
                return self.scrape(self.raw_song,
                                   self.meta_tags,
                                   tries_remaining=tries_remaining-1)

            youtubedetails = {'link': link, 'title': title, 'videotime': videotime,
                              'seconds': internals.get_sec(videotime)}
            videos.append(youtubedetails)

        if bestmatch:
            return self._best_match(videos)

        return videos