    def setBuddyShares(self, files, streams, wordindex, fileindex, mtimes):

        storable_objects = [
            (files, "bsharedfiles", "buddyfiles.db"),
            (streams, "bsharedfilesstreams", "buddystreams.db"),
            (mtimes, "bsharedmtimes", "buddymtimes.db"),
            (wordindex, "bwordindex", "buddywordindex.db"),
            (fileindex, "bfileindex", "buddyfileindex.db")
        ]

        self.storeObjects(storable_objects)