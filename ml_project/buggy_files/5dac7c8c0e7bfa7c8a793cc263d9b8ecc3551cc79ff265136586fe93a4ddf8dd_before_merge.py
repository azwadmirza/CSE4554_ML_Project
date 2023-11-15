    def housekeeping(self, expired_threshold, info_threshold):
        # delete 'closed' or 'expired' alerts older than "expired_threshold" hours
        # and 'informational' alerts older than "info_threshold" hours
        delete = """
            DELETE FROM alerts
             WHERE (status IN ('closed', 'expired')
                    AND last_receive_time < (NOW() at time zone 'utc' - INTERVAL '%(expired_threshold)s hours'))
                OR (severity='informational'
                    AND last_receive_time < (NOW() at time zone 'utc' - INTERVAL '%(info_threshold)s hours'))
        """
        self._delete(delete, {"expired_threshold": expired_threshold, "info_threshold": info_threshold})

        # get list of alerts to be newly expired
        update = """
            SELECT id, event, last_receive_id
              FROM alerts
             WHERE status NOT IN ('expired','shelved') AND timeout!=0
               AND (last_receive_time + INTERVAL '1 second' * timeout) < (NOW() at time zone 'utc')
        """
        expired = self._fetchall(update, {})

        # get list of alerts to be unshelved
        update = """
            SELECT id, event, last_receive_id
              FROM alerts
             WHERE status='shelved'
               AND (last_receive_time + INTERVAL '1 second' * timeout) < (NOW() at time zone 'utc')
        """
        unshelved = self._fetchall(update, {})

        return (expired, unshelved)