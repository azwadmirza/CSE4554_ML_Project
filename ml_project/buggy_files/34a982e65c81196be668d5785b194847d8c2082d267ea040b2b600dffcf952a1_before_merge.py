        def _cleanLocalTempDir(self, cacheSize):
            """
            At the end of the job, remove all localTempDir files except those whose value is in
            jobStoreFileIDToCacheLocation.
            
            The param cacheSize is the total number of bytes of files allowed in the cache.
            """
            #Remove files so that the total cached files are smaller than a cacheSize
            
            #List of pairs of (fileSize, fileStoreID) for cached files
            cachedFileSizes = map(lambda x : (os.stat(self.jobStoreFileIDToCacheLocation[x]).st_size, x), 
                                  self.jobStoreFileIDToCacheLocation.keys())
            #Total number of bytes stored in cached files
            totalCachedFileSizes = sum(map(lambda x : x[0], cachedFileSizes))
            #Remove smallest files first - this is not obviously best, could do it a different
            #way
            cachedFileSizes.sort()
            cachedFileSizes.reverse()
            #Now do the actual file removal
            while totalCachedFileSizes > cacheSize:
                fileSize, fileStoreID =  cachedFileSizes.pop()
                filePath = self.jobStoreFileIDToCacheLocation[fileStoreID]
                self.jobStoreFileIDToCacheLocation.pop(fileStoreID)
                os.remove(filePath)
                totalCachedFileSizes -= fileSize
                assert totalCachedFileSizes >= 0
            
            #Iterate from the base of localTempDir and remove all 
            #files/empty directories, recursively
            cachedFiles = set(self.jobStoreFileIDToCacheLocation.values())
            
            def clean(dirOrFile):
                canRemove = True 
                if os.path.isdir(dirOrFile):
                    for f in os.listdir(dirOrFile):
                        canRemove = canRemove and clean(os.path.join(dirOrFile, f))
                    if canRemove:
                        os.rmdir(dirOrFile) #Dir should be empty if canRemove is true
                    return canRemove
                if dirOrFile in cachedFiles:
                    return False
                os.remove(dirOrFile)
                return True    
            clean(self.localTempDir)