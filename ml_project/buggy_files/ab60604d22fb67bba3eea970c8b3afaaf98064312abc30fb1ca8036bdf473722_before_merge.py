    def parse_downloads(self, series_url, search_title):
        page = requests.get(series_url).content
        try:
            soup = get_soup(page)
        except Exception as e:
            raise UrlRewritingError(e)

        urls = []
        # find all titles
        episode_titles = self.find_all_titles(search_title)
        if not episode_titles:
            raise UrlRewritingError('Unable to find episode')

        for ep_title in episode_titles:
            # find matching download
            episode_title = soup.find('strong', text=re.compile(ep_title, re.I))
            if not episode_title:
                continue

            # find download container
            episode = episode_title.parent
            if not episode:
                continue

            # find episode language
            episode_lang = episode.find_previous('strong', text=re.compile('Sprache')).next_sibling
            if not episode_lang:
                log.warning('No language found for: %s' % series_url)
                continue

            # filter language
            if not self.check_language(episode_lang):
                log.warning('languages not matching: %s <> %s' % (self.config['language'], episode_lang))
                continue

            # find download links
            links = episode.find_all('a')
            if not links:
                log.warning('No links found for: %s' % series_url)
                continue

            for link in links:
                if not link.has_attr('href'):
                    continue

                url = link['href']
                pattern = 'http:\/\/download\.serienjunkies\.org.*%s_.*\.html' % self.config['hoster']

                if re.match(pattern, url) or self.config['hoster'] == 'all':
                    urls.append(url)
                else:
                    continue
        return urls