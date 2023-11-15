    def update_tracker_info(self, tracker_url, is_successful):
        """
        Updates a tracker information.
        :param tracker_url: The given tracker_url.
        :param is_successful: If the check was successful.
        """
        if tracker_url not in self._tracker_dict:
            self._logger.error("Trying to update the tracker info of an unknown tracker URL")
            return

        tracker_info = self._tracker_dict[tracker_url]

        current_time = int(time.time())
        failures = 0 if is_successful else tracker_info[u'failures'] + 1
        is_alive = tracker_info[u'failures'] < self._max_tracker_failures

        # update the dict
        tracker_info[u'last_check'] = current_time
        tracker_info[u'failures'] = failures
        tracker_info[u'is_alive'] = is_alive

        # update the database
        sql_stmt = u"UPDATE TrackerInfo SET last_check = ?, failures = ?, is_alive = ? WHERE tracker_id = ?"
        value_tuple = (tracker_info[u'last_check'], tracker_info[u'failures'], tracker_info[u'is_alive'],
                       tracker_info[u'id'])
        self._session.sqlite_db.execute(sql_stmt, value_tuple)