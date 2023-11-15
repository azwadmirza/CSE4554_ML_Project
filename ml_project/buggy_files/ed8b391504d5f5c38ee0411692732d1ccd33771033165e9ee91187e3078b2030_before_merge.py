    def _purge_trigger_instances(self):
        """
        Purge trigger instances which match the criteria defined in the config.
        """
        LOG.info('Performing garbage collection for trigger instances')

        utc_now = get_datetime_utc_now()
        timestamp = (utc_now - datetime.timedelta(days=self._trigger_instances_ttl))

        # Another sanity check to make sure we don't delete new executions
        if timestamp > (utc_now - datetime.timedelta(days=MINIMUM_TTL_DAYS)):
            raise ValueError('Calculated timestamp would violate the minimum TTL constraint')

        timestamp_str = isotime.format(dt=timestamp)
        LOG.info('Deleting trigger instances older than: %s' % (timestamp_str))

        assert timestamp < utc_now

        try:
            purge_trigger_instances(logger=LOG, timestamp=timestamp)
        except Exception as e:
            LOG.exception('Failed to trigger instances: %s' % (six.text_type(e)))

        return True