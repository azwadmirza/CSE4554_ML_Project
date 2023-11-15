        def writeGlobalFile(self, localFileName, cleanup=False):
            """
            Takes a file (as a path) and uploads it to the job store. 
            
            If the local file is a file returned by :func:`toil.job.Job.FileStore.getLocalTempFile` \
            or is in a directory, or, recursively, a subdirectory, returned by \
            :func:`toil.job.Job.FileStore.getLocalTempDir` then the write is asynchronous, \
            so further modifications during execution to the file pointed by \
            localFileName will result in undetermined behavior. Otherwise, the \
            method will block until the file is written to the file store. 
            
            :param string localFileName: The path to the local file to upload.
            
            :param Boolean cleanup: if True then the copy of the global file will \
            be deleted once the job and all its successors have completed running. \
            If not the global file must be deleted manually.
            
            :returns: an ID that can be used to retrieve the file. 
            """
            #Put the file into the cache if it is a path within localTempDir
            absLocalFileName = os.path.abspath(localFileName)
            cleanupID = None if not cleanup else self.jobWrapper.jobStoreID
            if absLocalFileName.startswith(self.localTempDir):
                jobStoreFileID = self.jobStore.getEmptyFileStoreID(cleanupID)
                fileHandle = open(absLocalFileName, 'r')
                if os.stat(absLocalFileName).st_uid == os.getuid():
                    #Chmod if permitted to make file read only to try to prevent accidental user modification
                    os.chmod(absLocalFileName, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
                with self._lockFilesLock:
                    self._lockFiles.add(jobStoreFileID)
                # A file handle added to the queue allows the asyncWrite threads to remove their jobID from _lockFiles.
                # Therefore, a file should only be added after its fileID is added to _lockFiles
                self.queue.put((fileHandle, jobStoreFileID))
                self._jobStoreFileIDToCacheLocation[jobStoreFileID] = absLocalFileName
            else:
                #Write the file directly to the file store
                jobStoreFileID = self.jobStore.writeFile(localFileName, cleanupID)
            return jobStoreFileID