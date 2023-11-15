    def run(self):
        LOG.debug('Starting scheduler handler...')

        while not self._shutdown:
            eventlet.greenthread.sleep(cfg.CONF.scheduler.sleep_interval)
            self.process()