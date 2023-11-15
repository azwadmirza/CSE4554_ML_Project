    def readStatsAndLogging(self, callback, readAll=False):
        suffix = '_old'
        numStatsFiles = 0
        for entity in self.statsFileIDs.query_entities():
            jobStoreFileID = entity.RowKey
            hasBeenRead = len(jobStoreFileID) > self.jobIDLength
            if not hasBeenRead:
                with self._downloadStream(jobStoreFileID, self.statsFiles) as fd:
                    callback(fd)
                # Mark this entity as read by appending the suffix
                self.statsFileIDs.insert_entity(entity={'RowKey': jobStoreFileID + suffix})
                self.statsFileIDs.delete_entity(row_key=jobStoreFileID)
                numStatsFiles += 1
            elif readAll:
                # Strip the suffix to get the original ID
                jobStoreFileID = jobStoreFileID[:-len(suffix)]
                with self._downloadStream(jobStoreFileID, self.statsFiles) as fd:
                    callback(fd)
                numStatsFiles += 1
        return numStatsFiles