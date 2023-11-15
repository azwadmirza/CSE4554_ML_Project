    def flush(self, retry=3, write_batch=None):
        if not write_batch and self._pending_torrents:
            write_batch = self._writebatch(self._db)
            for k, v in self._pending_torrents.iteritems():
                write_batch.Put(k, v)
            self._pending_torrents.clear()

        if write_batch:
            if not retry:
                self._logger.error("Failed to flush LevelDB cache. Max retry done.")
                return
            try:
                self._db.Write(write_batch)
            except Exception as ex:
                self._logger.error("Failed to flush LevelDB cache. Will retry %s times. Error:%s", retry-1, ex)
                self.flush(retry=retry-1, write_batch=write_batch)