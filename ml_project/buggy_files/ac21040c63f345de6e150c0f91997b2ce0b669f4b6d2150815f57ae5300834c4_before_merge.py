        def writeGlobalFile(self, localFileName, cleanup=False):
            """
            Takes a file (as a path) and uploads it to to the global file store, 
            returns an ID that can be used to retrieve the file. 
            
            If cleanup is True then the global file will be deleted once the job
            and all its successors have completed running. If not the global file 
            must be deleted manually.
            
            The write is asynchronous, so further modifications during execution 
            to the file pointed by localFileName will result in undetermined behavior. 
            """
            jobStoreFileID = self.jobStore.getEmptyFileStoreID(None 
                            if not cleanup else self.jobWrapper.jobStoreID)
            self.queue.put((open(localFileName, 'r'), jobStoreFileID))
            #Now put the file into the cache if it is a path within localTempDir
            absLocalFileName = os.path.abspath(localFileName)
            if absLocalFileName.startswith(self.localTempDir):
                #Chmod to make file read only
                os.chmod(absLocalFileName, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
                self.jobStoreFileIDToCacheLocation[jobStoreFileID] = absLocalFileName
            return jobStoreFileID