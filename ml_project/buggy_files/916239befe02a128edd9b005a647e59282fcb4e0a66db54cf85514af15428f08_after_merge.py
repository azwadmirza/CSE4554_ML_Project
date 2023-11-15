    def run(self, force=False):  # pylint: disable=too-many-branches, too-many-statements, too-many-locals
        """Checks for needed subtitles for users' shows

        :param force: True if a force search needs to be executed
        :type force: bool
        """
        if not sickbeard.USE_SUBTITLES:
            return

        if not sickbeard.subtitles.enabled_service_list():
            logger.log(u'Not enough services selected. At least 1 service is required to '
                       u'search subtitles in the background', logger.WARNING)
            return

        self.amActive = True

        def dhm(td):
            days = td.days
            hours = td.seconds // 60 ** 2
            minutes = (td.seconds // 60) % 60
            ret = (u'', '{} days, '.format(days))[days > 0] + \
                  (u'', '{} hours, '.format(hours))[hours > 0] + \
                  (u'', '{} minutes'.format(minutes))[minutes > 0]
            if days == 1:
                ret = ret.replace('days', 'day')
            if hours == 1:
                ret = ret.replace('hours', 'hour')
            if minutes == 1:
                ret = ret.replace('minutes', 'minute')
            return ret.rstrip(', ')

        if sickbeard.SUBTITLES_DOWNLOAD_IN_PP:
            self.subtitles_download_in_pp()

        logger.log(u'Checking for missed subtitles', logger.INFO)

        database = db.DBConnection()
        # Shows with air date <= 30 days, have a limit of 100 results
        # Shows with air date > 30 days, have a limit of 200 results
        sql_args = [{'age_comparison': '<=', 'limit': 100}, {'age_comparison': '>', 'limit': 200}]
        sql_like_languages = '%' + ','.join(sorted(wanted_languages())) + '%' if sickbeard.SUBTITLES_MULTI else '%und%'
        sql_results = []
        for args in sql_args:
            sql_results += database.select(
                "SELECT "
                "   s.show_name, "
                "   e.showid, "
                "   e.season, "
                "   e.episode,"
                "   e.release_name, "
                "   e.status, "
                "   e.subtitles, "
                "   e.subtitles_searchcount AS searchcount, "
                "   e.subtitles_lastsearch AS lastsearch, "
                "   e.location, (? - e.airdate) as age "
                "FROM "
                "   tv_episodes AS e "
                "INNER JOIN "
                "   tv_shows AS s "
                "ON (e.showid = s.indexer_id) "
                "WHERE"
                "   s.subtitles = 1 "
                "   AND (e.status LIKE '%4' OR e.status LIKE '%6') "
                "   AND e.season > 0 "
                "   AND e.location != '' "
                "   AND age {} 30 "
                "   AND e.subtitles NOT LIKE ? "
                "ORDER BY "
                "   lastsearch ASC "
                "LIMIT {}".format
                (args['age_comparison'], args['limit']), [datetime.datetime.now().toordinal(), sql_like_languages]
            )

        if not sql_results:
            logger.log(u'No subtitles to download', logger.INFO)
            self.amActive = False
            return

        for ep_to_sub in sql_results:
            ep_num = episode_num(ep_to_sub['season'], ep_to_sub['episode']) or \
                     episode_num(ep_to_sub['season'], ep_to_sub['episode'], numbering='absolute')
            subtitle_path = encode(ep_to_sub['location'], encoding=sickbeard.SYS_ENCODING, fallback='utf-8')
            if not os.path.isfile(subtitle_path):
                logger.log(u'Episode file does not exist, cannot download subtitles for {0} {1}'.format
                           (ep_to_sub['show_name'], ep_num), logger.DEBUG)
                continue

            if not needs_subtitles(ep_to_sub['subtitles']):
                logger.log(u'Episode already has all needed subtitles, skipping {0} {1}'.format
                           (ep_to_sub['show_name'], ep_num), logger.DEBUG)
                continue

            try:
                lastsearched = datetime.datetime.strptime(ep_to_sub['lastsearch'], dateTimeFormat)
            except ValueError:
                lastsearched = datetime.datetime.min

            try:
                if not force:
                    now = datetime.datetime.now()
                    days = int(ep_to_sub['age'])
                    delay_time = datetime.timedelta(hours=1 if days <= 10 else 8 if days <= 30 else 30 * 24)
                    delay = lastsearched + delay_time - now

                    # Search every hour until 10 days pass
                    # After 10 days, search every 8 hours, after 30 days search once a month
                    # Will always try an episode regardless of age for 3 times
                    # The time resolution is minute
                    # Only delay is the it's bigger than one minute and avoid wrongly skipping the search slot.
                    if delay.total_seconds() > 60 and int(ep_to_sub['searchcount']) > 2:
                        logger.log(u'Subtitle search for {0} {1} delayed for {2}'.format
                                   (ep_to_sub['show_name'], ep_num, dhm(delay)), logger.DEBUG)
                        continue

                show_object = Show.find(sickbeard.showList, int(ep_to_sub['showid']))
                if not show_object:
                    logger.log(u'Show with ID {0} not found in the database'.format(ep_to_sub['showid']), logger.DEBUG)
                    continue

                episode_object = show_object.getEpisode(ep_to_sub['season'], ep_to_sub['episode'])
                if isinstance(episode_object, str):
                    logger.log(u'{0} {1} not found in the database'.format
                               (ep_to_sub['show_name'], ep_num), logger.DEBUG)
                    continue

                try:
                    episode_object.download_subtitles()
                except Exception as error:
                    logger.log(u'Unable to find subtitles for {0} {1}. Error: {2}'.format
                               (ep_to_sub['show_name'], ep_num, ex(error)), logger.ERROR)
                    continue

            except Exception as error:
                logger.log(u'Error while searching subtitles for {0} {1}. Error: {2}'.format
                           (ep_to_sub['show_name'], ep_num, ex(error)), logger.WARNING)
                continue

        logger.log(u'Finished checking for missed subtitles', logger.INFO)
        self.amActive = False