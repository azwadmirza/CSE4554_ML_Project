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
        select = """
            SELECT id, event, last_receive_id
              FROM alerts
             WHERE status NOT IN ('expired','shelved') AND timeout!=0
               AND (last_receive_time + INTERVAL '1 second' * timeout) < (NOW() at time zone 'utc')
        """
        expired = self._fetchall(select, {})

        # get list of alerts to be unshelved
        select = """
        WITH shelved AS (
            SELECT DISTINCT ON (a.id) a.id, a.event, a.last_receive_id, h.update_time, a.timeout
              FROM alerts a, UNNEST(history) h
             WHERE a.status='shelved'
               AND h.type='action'
               AND h.status='shelved'
          ORDER BY a.id, h.update_time DESC
        )
        SELECT id, event, last_receive_id
          FROM shelved
         WHERE (update_time + INTERVAL '1 second' * timeout) < (NOW() at time zone 'utc')
        """
        unshelved = self._fetchall(select, {})

        return (expired, unshelved)