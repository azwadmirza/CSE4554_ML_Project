    def get_tracker_info(self, tracker_url):
        """
        Gets the tracker information with the given tracker URL.
        :param tracker_url: The given tracker URL.
        :return: The tracker info dict if exists, None otherwise.
        """
        sanitized_tracker_url = get_uniformed_tracker_url(tracker_url) if tracker_url != u"DHT" else tracker_url
        try:
            sql_stmt = u"SELECT tracker_id, tracker, last_check, failures, is_alive FROM TrackerInfo WHERE tracker = ?"
            result = self._session.sqlite_db.execute(sql_stmt, (sanitized_tracker_url,)).next()
        except StopIteration:
            return None

        return {u'id': result[0], u'last_check': result[2], u'failures': result[3], u'is_alive': bool(result[4])}