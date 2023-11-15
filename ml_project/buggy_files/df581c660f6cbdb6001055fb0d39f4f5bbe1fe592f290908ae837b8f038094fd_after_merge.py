    def setShares(self, files, streams, wordindex, fileindex, mtimes):

        storable_objects = [
            (files, "sharedfiles", "files.db"),
            (streams, "sharedfilesstreams", "streams.db"),
            (mtimes, "sharedmtimes", "mtimes.db"),
            (wordindex, "wordindex", "wordindex.db"),
            (fileindex, "fileindex", "fileindex.db")
        ]

        self.storeObjects(storable_objects)