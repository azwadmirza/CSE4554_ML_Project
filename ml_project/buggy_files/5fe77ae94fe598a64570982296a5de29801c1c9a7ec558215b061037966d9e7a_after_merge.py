    def add_tracker(self, tracker_url):
        """
        Adds a new tracker into the tracker info dict and the database.
        :param tracker_url: The new tracker URL to be added.
        """
        sanitized_tracker_url = get_uniformed_tracker_url(tracker_url)
        if sanitized_tracker_url is None:
            self._logger.warn(u"skip invalid tracker: %s", repr(tracker_url))
            return

        sql_stmt = u"SELECT COUNT() FROM TrackerInfo WHERE tracker = ?"
        num = self._session.sqlite_db.execute(sql_stmt, (sanitized_tracker_url,)).next()[0]
        if num > 0:
            self._logger.debug(u"skip existing tracker: %s", repr(tracker_url))
            return

        # add the tracker into dict and database
        tracker_info = {u'last_check': 0,
                        u'failures': 0,
                        u'is_alive': True}

        # insert into database
        sql_stmt = u"""INSERT INTO TrackerInfo(tracker, last_check, failures, is_alive) VALUES(?,?,?,?);
                       SELECT tracker_id FROM TrackerInfo WHERE tracker = ?;
                    """
        value_tuple = (sanitized_tracker_url, tracker_info[u'last_check'], tracker_info[u'failures'],
                       tracker_info[u'is_alive'], sanitized_tracker_url)
        self._session.sqlite_db.execute(sql_stmt, value_tuple).next()