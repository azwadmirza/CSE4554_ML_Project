    def update_tracker_info(self, tracker_url, is_successful):
        """
        Updates a tracker information.
        :param tracker_url: The given tracker_url.
        :param is_successful: If the check was successful.
        """

        if tracker_url == u"DHT":
            return

        sanitized_tracker_url = get_uniformed_tracker_url(tracker_url)
        tracker = self.tracker_store.get(lambda g: g.url == sanitized_tracker_url)

        if not tracker:
            self._logger.error("Trying to update the tracker info of an unknown tracker URL")
            return

        current_time = int(time.time())
        failures = 0 if is_successful else tracker.failures + 1
        is_alive = failures < MAX_TRACKER_FAILURES

        # update the dict
        tracker.last_check = current_time
        tracker.failures = failures
        tracker.alive = is_alive