    def _purge_action_executions(self):
        """
        Purge action executions and corresponding live action, stdout and stderr object which match
        the criteria defined in the config.
        """
        LOG.info('Performing garbage collection for action executions and related objects')

        utc_now = get_datetime_utc_now()
        timestamp = (utc_now - datetime.timedelta(days=self._action_executions_ttl))

        # Another sanity check to make sure we don't delete new executions
        if timestamp > (utc_now - datetime.timedelta(days=MINIMUM_TTL_DAYS)):
            raise ValueError('Calculated timestamp would violate the minimum TTL constraint')

        timestamp_str = isotime.format(dt=timestamp)
        LOG.info('Deleting action executions older than: %s' % (timestamp_str))

        assert timestamp < utc_now

        try:
            purge_executions(logger=LOG, timestamp=timestamp)
        except Exception as e:
            LOG.exception('Failed to delete executions: %s' % (six.text_type(e)))

        return True