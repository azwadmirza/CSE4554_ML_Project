    def _get_schedulers(self):
        schedulers = [s.key.rsplit('/', 1)[1] for s in self._client.read(SCHEDULER_PATH).children]
        logger.debug('Schedulers obtained. Results: %r', schedulers)
        return schedulers