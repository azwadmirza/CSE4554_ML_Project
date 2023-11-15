    def get_next_tracker_for_auto_check(self):
        """
        Gets the next tracker for automatic tracker-checking.
        :return: The next tracker for automatic tracker-checking.
        """
        try:
            sql_stmt = u"SELECT tracker FROM TrackerInfo WHERE tracker != 'no-DHT' AND tracker != 'DHT' AND " \
                       u"last_check + ? <= strftime('%s','now') AND is_alive = 1 ORDER BY last_check LIMIT 1;"
            result = self._session.sqlite_db.execute(sql_stmt, (TRACKER_RETRY_INTERVAL,)).next()
        except StopIteration:
            return None

        return result[0]