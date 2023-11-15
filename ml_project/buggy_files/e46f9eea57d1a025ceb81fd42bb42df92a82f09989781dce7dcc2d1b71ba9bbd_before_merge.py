    def flush(self):
        if self._pending_torrents:
            write_batch = self._writebatch(self._db)
            for k, v in self._pending_torrents.iteritems():
                write_batch.Put(k, v)
            self._pending_torrents.clear()
            return self._db.Write(write_batch)