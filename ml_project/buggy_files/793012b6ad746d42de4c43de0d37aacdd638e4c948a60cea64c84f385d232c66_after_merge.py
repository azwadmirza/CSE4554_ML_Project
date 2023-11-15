    async def check_random_tracker(self):
        """
        Calling this method will fetch a random tracker from the database, select some torrents that have this
        tracker, and perform a request to these trackers.
        Return whether the check was successful.
        """
        if self._should_stop:
            self._logger.warning("Not performing tracker check since we are shutting down")
            return False

        tracker = self.get_valid_next_tracker_for_auto_check()
        if tracker is None:
            self._logger.warning(u"No tracker to select from, skip")
            return False

        self._logger.debug(u"Start selecting torrents on tracker %s.", tracker.url)

        # get the torrents that should be checked
        with db_session:
            dynamic_interval = TORRENT_CHECK_RETRY_INTERVAL * (2 ** tracker.failures)
            # FIXME: this is a really dumb fix for update_tracker_info not being called in some cases
            if tracker.failures >= MAX_TRACKER_FAILURES:
                self.update_tracker_info(tracker.url, False)
                return False
            torrents = select(ts for ts in tracker.torrents if ts.last_check + dynamic_interval < int(time.time()))
            infohashes = [t.infohash for t in torrents[:MAX_TORRENTS_CHECKED_PER_SESSION]]

        if len(infohashes) == 0:
            # We have no torrent to recheck for this tracker. Still update the last_check for this tracker.
            self._logger.info("No torrent to check for tracker %s", tracker.url)
            self.update_tracker_info(tracker.url, True)
            return False

        try:
            session = self._create_session_for_request(tracker.url, timeout=30)
        except MalformedTrackerURLException as e:
            # Remove the tracker from the database
            self.remove_tracker(tracker.url)
            self._logger.error(e)
            return False

        # We shuffle the list so that different infohashes are checked on subsequent scrape requests if the total
        # number of infohashes exceeds the maximum number of infohashes we check.
        random.shuffle(infohashes)
        for infohash in infohashes:
            session.add_infohash(infohash)

        self._logger.info(u"Selected %d new torrents to check on tracker: %s", len(infohashes), tracker.url)
        try:
            await self.connect_to_tracker(session)
            return True
        except:
            return False