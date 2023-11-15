    def readStatsAndLogging(self, statsAndLoggingCallbackFn):
        numStatsFiles = 0
        for entity in self.statsFileIDs.query_entities():
            jobStoreFileID = entity.RowKey
            with self._downloadStream(jobStoreFileID, self.statsFiles) as fd:
                statsAndLoggingCallbackFn(fd)
            self.statsFiles.delete_blob(blob_name=jobStoreFileID)
            self.statsFileIDs.delete_entity(row_key=jobStoreFileID)
            numStatsFiles += 1
        return numStatsFiles