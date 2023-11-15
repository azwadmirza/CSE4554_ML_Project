    def feed_all(self, masterid):
        for scanid in self.get_scans():
            try:
                self.feed(masterid, scanid)
            except LockError:
                utils.LOGGER.error(
                    'Lock error - is another daemon process running?',
                    exc_info=True,
                )