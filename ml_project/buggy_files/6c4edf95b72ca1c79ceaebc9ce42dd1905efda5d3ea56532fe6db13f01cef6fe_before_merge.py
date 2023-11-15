    def setBuddyShares(self, files, streams, wordindex, fileindex, mtimes):

        storable_objects = [
            (files, "bsharedfiles", "buddyfiles.db"),
            (streams, "bsharedfilesstreams", "buddystreams.db"),
            (mtimes, "bsharedmtimes", "buddymtimes.db"),
            (wordindex, "bwordindex", "buddywordindex.db"),
            (fileindex, "bfileindex", "buddyfileindex.db")
        ]

        self.config_lock.acquire()
        _thread.start_new_thread(self._storeObjects, (storable_objects,))
        self.config_lock.release()