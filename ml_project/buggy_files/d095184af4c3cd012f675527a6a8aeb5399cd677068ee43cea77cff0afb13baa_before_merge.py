    def _purge_action_executions_output(self):
        LOG.info('Performing garbage collection for action executions output objects')

        utc_now = get_datetime_utc_now()
        timestamp = (utc_now - datetime.timedelta(days=self._action_executions_output_ttl))

        # Another sanity check to make sure we don't delete new objects
        if timestamp > (utc_now - datetime.timedelta(days=MINIMUM_TTL_DAYS_EXECUTION_OUTPUT)):
            raise ValueError('Calculated timestamp would violate the minimum TTL constraint')

        timestamp_str = isotime.format(dt=timestamp)
        LOG.info('Deleting action executions output objects older than: %s' % (timestamp_str))

        assert timestamp < utc_now

        try:
            purge_execution_output_objects(logger=LOG, timestamp=timestamp)
        except Exception as e:
            LOG.exception('Failed to delete execution output objects: %s' % (six.text_type(e)))

        return True