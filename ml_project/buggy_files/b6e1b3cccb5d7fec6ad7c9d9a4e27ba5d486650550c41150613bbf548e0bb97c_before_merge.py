    def _task_select_tracker(self):
        """
        The regularly scheduled task that selects torrents associated with a specific tracker to check.
        """

        # update the torrent selection interval
        self._reschedule_tracker_select()

        # start selecting torrents
        result = self.tribler_session.lm.tracker_manager.get_next_tracker_for_auto_check()
        if result is None:
            self._logger.warn(u"No tracker to select from, skip")
            return succeed(None)

        tracker_url, _ = result
        self._logger.debug(u"Start selecting torrents on tracker %s.", tracker_url)

        # get the torrents that should be checked
        infohashes = self._torrent_db.getTorrentsOnTracker(tracker_url, int(time.time()))

        if len(infohashes) == 0:
            # We have not torrent to recheck for this tracker. Still update the last_check for this tracker.
            self._logger.info("No torrent to check for tracker %s", tracker_url)
            self.tribler_session.lm.tracker_manager.update_tracker_info(tracker_url, True)
            return succeed(None)
        elif tracker_url != u'DHT' and tracker_url != u'no-DHT'\
                and self.tribler_session.lm.tracker_manager.should_check_tracker(tracker_url):
            session = self._create_session_for_request(tracker_url, timeout=30)
            for infohash in infohashes:
                session.add_infohash(infohash)

            self._logger.info(u"Selected %d new torrents to check on tracker: %s", len(infohashes), tracker_url)
            return session.connect_to_tracker().addCallbacks(*self.get_callbacks_for_session(session))\
                .addErrback(lambda _: None)