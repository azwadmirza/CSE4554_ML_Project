    def download_subtitles(self, lang=None):
        """Download subtitles.

        :param lang:
        :type lang: string
        """
        if not self.is_location_valid():
            logger.debug("{id}: {show} {ep} file doesn't exist, can't download subtitles",
                         id=self.show.indexerid, show=self.show.name,
                         ep=(episode_num(self.season, self.episode) or episode_num(self.season, self.episode,
                                                                                   numbering='absolute')))
            return

        new_subtitles = subtitles.download_subtitles(self, lang=lang)
        if new_subtitles:
            self.subtitles = subtitles.merge_subtitles(self.subtitles, new_subtitles)

        self.subtitles_searchcount += 1 if self.subtitles_searchcount else 1
        self.subtitles_lastsearch = datetime.datetime.now().strftime(dateTimeFormat)
        logger.debug('{id}: Saving last subtitles search to database', id=self.show.indexerid)
        self.save_to_db()

        if new_subtitles:
            subtitle_list = ', '.join([subtitles.name_from_code(code) for code in new_subtitles])
            logger.info('{id}: Downloaded {subs} subtitles for {show} {ep}',
                        id=self.show.indexerid, subs=subtitle_list, show=self.show.name,
                        ep=(episode_num(self.season, self.episode) or
                            episode_num(self.season, self.episode, numbering='absolute')))

            try:
                notifiers.notify_subtitle_download(self.pretty_name(), subtitle_list)
            except RequestException as e:
                logger.debug(u'Unable to send subtitle download notification. Error: {error}', error=e.message)
        else:
            logger.info('{id}: No subtitles found for {show} {ep}',
                        id=self.show.indexerid, show=self.show.name,
                        ep=(episode_num(self.season, self.episode) or
                            episode_num(self.season, self.episode, numbering='absolute')))

        return new_subtitles