    def clean_session(self, session):
        self.tribler_session.lm.tracker_manager.update_tracker_info(session.tracker_url, not session.is_failed)
        self.session_stop_defer_list.append(session.cleanup())

        # Remove the session from our session list dictionary
        self._session_list[session.tracker_url].remove(session)
        if len(self._session_list[session.tracker_url]) == 0 and session.tracker_url != u"DHT":
            del self._session_list[session.tracker_url]