    def run(self):
        LOG.debug('Entering scheduler loop')

        while not self._shutdown:
            eventlet.greenthread.sleep(cfg.CONF.scheduler.sleep_interval)

            execution_queue_item_db = self._get_next_execution()

            if execution_queue_item_db:
                self._pool.spawn(self._handle_execution, execution_queue_item_db)