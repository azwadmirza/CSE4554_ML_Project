    async def check_random_tracker(self):
        """
        Calling this method will fetch a random tracker from the database, select some torrents that have this
        tracker, and perform a request to these trackers.
        """
        tracker_url = self.get_valid_next_tracker_for_auto_check()
        if tracker_url is None:
            self._logger.warning(u"No tracker to select from, skip")
            return

        self._logger.debug(u"Start selecting torrents on tracker %s.", tracker_url)

        # get the torrents that should be checked
        with db_session:
            tracker = self.tribler_session.mds.TrackerState.get(url=tracker_url)
            if not tracker:
                return
            dynamic_interval = TORRENT_CHECK_RETRY_INTERVAL * (2 ** tracker.failures)
            # FIXME: this is a really dumb fix for update_tracker_info not being called in some cases
            if tracker.failures >= MAX_TRACKER_FAILURES:
                tracker.alive = False
                return
            torrents = select(ts for ts in tracker.torrents if ts.last_check + dynamic_interval < int(time.time()))
            infohashes = [t.infohash for t in torrents[:MAX_TORRENTS_CHECKED_PER_SESSION]]

        if len(infohashes) == 0:
            # We have no torrent to recheck for this tracker. Still update the last_check for this tracker.
            self._logger.info("No torrent to check for tracker %s", tracker_url)
            self.update_tracker_info(tracker_url, True)
            return

        try:
            session = self._create_session_for_request(tracker_url, timeout=30)
        except MalformedTrackerURLException as e:
            # Remove the tracker from the database
            self.remove_tracker(tracker_url)
            self._logger.error(e)
            return

        # We shuffle the list so that different infohashes are checked on subsequent scrape requests if the total
        # number of infohashes exceeds the maximum number of infohashes we check.
        random.shuffle(infohashes)
        for infohash in infohashes:
            session.add_infohash(infohash)

        self._logger.info(u"Selected %d new torrents to check on tracker: %s", len(infohashes), tracker_url)
        try:
            await self.connect_to_tracker(session)
        except:
            pass