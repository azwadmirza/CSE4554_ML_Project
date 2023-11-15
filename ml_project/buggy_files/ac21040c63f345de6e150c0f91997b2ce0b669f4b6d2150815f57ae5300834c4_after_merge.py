        def writeGlobalFile(self, localFileName, cleanup=False):
            """
            Takes a file (as a path) and uploads it to to the global file store, 
            returns an ID that can be used to retrieve the file. 
            
            If cleanup is True then the global file will be deleted once the job
            and all its successors have completed running. If not the global file 
            must be deleted manually.
            
            If the local file is a file returned by Job.FileStore.getLocalTempFile
            or is in a directory, or, recursively, a subdirectory, returned by 
            Job.FileStore.getLocalTempDir then the write is asynchronous, 
            so further modifications during execution to the file pointed by 
            localFileName will result in undetermined behavior. Otherwise, the 
            method will block until the file is written to the file store. 
            """
            #Put the file into the cache if it is a path within localTempDir
            absLocalFileName = os.path.abspath(localFileName)
            cleanupID = None if not cleanup else self.jobWrapper.jobStoreID
            if absLocalFileName.startswith(self.localTempDir):
                jobStoreFileID = self.jobStore.getEmptyFileStoreID(cleanupID)
                self.queue.put((open(absLocalFileName, 'r'), jobStoreFileID))
                #Chmod to make file read only to try to prevent accidental user modification
                os.chmod(absLocalFileName, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
                self.jobStoreFileIDToCacheLocation[jobStoreFileID] = absLocalFileName
            else:
                #Write the file directly to the file store
                jobStoreFileID = self.jobStore.writeFile(localFileName, cleanupID)
            return jobStoreFileID