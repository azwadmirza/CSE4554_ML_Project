    def _perform_garbage_collection(self):
        LOG.info('Performing garbage collection...')

        # Note: We sleep for a bit between garbage collection of each object type to prevent busy
        # waiting
        if self._action_executions_ttl and self._action_executions_ttl >= MINIMUM_TTL_DAYS:
            self._purge_action_executions()
            eventlet.sleep(self._sleep_delay)
        else:
            LOG.debug('Skipping garbage collection for action executions since it\'s not '
                      'configured')

        if self._action_executions_output_ttl and \
                self._action_executions_output_ttl >= MINIMUM_TTL_DAYS_EXECUTION_OUTPUT:
            self._purge_action_executions_output()
            eventlet.sleep(self._sleep_delay)
        else:
            LOG.debug('Skipping garbage collection for action executions output since it\'s not '
                      'configured')

        if self._trigger_instances_ttl and self._trigger_instances_ttl >= MINIMUM_TTL_DAYS:
            self._purge_trigger_instances()
            eventlet.sleep(self._sleep_delay)
        else:
            LOG.debug('Skipping garbage collection for trigger instances since it\'s not '
                      'configured')

        if self._purge_inquiries:
            self._timeout_inquiries()
            eventlet.sleep(self._sleep_delay)
        else:
            LOG.debug('Skipping garbage collection for Inquiries since it\'s not '
                      'configured')