    def is_page_candidate(self, url_link, url_title, title, artist):
        """Return True if the URL title makes it a good candidate to be a
        page that contains lyrics of title by artist.
        """
        title = self.slugify(title.lower())
        artist = self.slugify(artist.lower())
        sitename = re.search(u"//([^/]+)/.*",
                             self.slugify(url_link.lower())).group(1)
        url_title = self.slugify(url_title.lower())

        # Check if URL title contains song title (exact match)
        if url_title.find(title) != -1:
            return True

        # or try extracting song title from URL title and check if
        # they are close enough
        tokens = [by + '_' + artist for by in self.BY_TRANS] + \
                 [artist, sitename, sitename.replace('www.', '')] + \
            self.LYRICS_TRANS
        tokens = [re.escape(t) for t in tokens]
        song_title = re.sub(u'(%s)' % u'|'.join(tokens), u'', url_title)

        song_title = song_title.strip('_|')
        typo_ratio = .9
        ratio = difflib.SequenceMatcher(None, song_title, title).ratio()
        return ratio >= typo_ratio