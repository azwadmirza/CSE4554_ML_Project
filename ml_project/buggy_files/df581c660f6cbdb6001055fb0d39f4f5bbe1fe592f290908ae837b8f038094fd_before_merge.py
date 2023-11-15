    def setShares(self, files, streams, wordindex, fileindex, mtimes):

        storable_objects = [
            (files, "sharedfiles", "files.db"),
            (streams, "sharedfilesstreams", "streams.db"),
            (mtimes, "sharedmtimes", "mtimes.db"),
            (wordindex, "wordindex", "wordindex.db"),
            (fileindex, "fileindex", "fileindex.db")
        ]

        self.config_lock.acquire()
        _thread.start_new_thread(self._storeObjects, (storable_objects,))
        self.config_lock.release()