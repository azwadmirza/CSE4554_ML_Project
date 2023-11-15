    def cleanup(self):
        LOG.debug('Starting scheduler garbage collection...')

        while not self._shutdown:
            eventlet.greenthread.sleep(cfg.CONF.scheduler.gc_interval)
            self._handle_garbage_collection()