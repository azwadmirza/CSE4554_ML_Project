    def on_session_error(self, session, failure):
        """
        Handles the scenario of when a tracker session has failed by calling the
        tracker_manager's update_tracker_info function.
        Trap value errors that are thrown by e.g. the HTTPTrackerSession when a connection fails.
        And trap CancelledErrors that can be thrown when shutting down.
        :param failure: The failure object raised by Twisted.
        """
        failure.trap(ValueError, CancelledError, ConnectingCancelledError, RuntimeError)
        self._logger.warning(u"Got session error for URL %s: %s", session.tracker_url, failure)

        # Do not update if the connection got cancelled, we are probably shutting down
        # and the tracker_manager may have shutdown already.
        if failure.check(CancelledError, ConnectingCancelledError) is None:
            self.tribler_session.lm.tracker_manager.update_tracker_info(session.tracker_url, False)

        failure.tracker_url = session.tracker_url
        return failure