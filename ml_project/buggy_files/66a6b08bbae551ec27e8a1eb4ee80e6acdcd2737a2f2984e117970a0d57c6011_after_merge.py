    def _configure(self):
        try:
            self.store = storage.get_driver(self.conf)
            self.index = indexer.get_driver(self.conf)
            self.index.connect()
        except Exception as e:
            raise utils.Retry(e)