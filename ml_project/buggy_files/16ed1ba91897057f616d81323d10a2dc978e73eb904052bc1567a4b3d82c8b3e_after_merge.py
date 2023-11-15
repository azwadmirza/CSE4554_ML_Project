    def _perform_garbage_collection(self):
        LOG.info('Performing garbage collection...')

        proc_message = "Performing garbage collection for %s."
        skip_message = "Skipping garbage collection for %s since it's not configured."

        # Note: We sleep for a bit between garbage collection of each object type to prevent busy
        # waiting
        obj_type = 'action executions'
        if self._action_executions_ttl and self._action_executions_ttl >= MINIMUM_TTL_DAYS:
            LOG.info(proc_message, obj_type)
            self._purge_action_executions()
            eventlet.sleep(self._sleep_delay)
        else:
            LOG.debug(skip_message, obj_type)

        obj_type = 'action executions output'
        if self._action_executions_output_ttl and \
                self._action_executions_output_ttl >= MINIMUM_TTL_DAYS_EXECUTION_OUTPUT:
            LOG.info(proc_message, obj_type)
            self._purge_action_executions_output()
            eventlet.sleep(self._sleep_delay)
        else:
            LOG.debug(skip_message, obj_type)

        obj_type = 'trigger instances'
        if self._trigger_instances_ttl and self._trigger_instances_ttl >= MINIMUM_TTL_DAYS:
            LOG.info(proc_message, obj_type)
            self._purge_trigger_instances()
            eventlet.sleep(self._sleep_delay)
        else:
            LOG.debug(skip_message, obj_type)

        obj_type = 'inquiries'
        if self._purge_inquiries:
            LOG.info(proc_message, obj_type)
            self._timeout_inquiries()
            eventlet.sleep(self._sleep_delay)
        else:
            LOG.debug(skip_message, obj_type)

        obj_type = 'orphaned workflow executions'
        if self._workflow_execution_max_idle > 0:
            LOG.info(proc_message, obj_type)
            self._purge_orphaned_workflow_executions()
            eventlet.sleep(self._sleep_delay)
        else:
            LOG.debug(skip_message, obj_type)