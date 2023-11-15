        def readGlobalFile(self, fileStoreID, userPath=None):
            """
            Returns an absolute path to a local, temporary copy of the file 
            keyed by fileStoreID. 
            
            *The returned file will be read only (have permissions 444).* 
            
            :param userPath: a path to the name of file to which the global file will be 
            copied or hard-linked (see below). userPath must either be: (1) a 
            file path contained within a directory or, recursively, a subdirectory 
            of a temporary directory returned by Job.FileStore.getLocalTempDir(), 
            or (2) a file path returned by Job.FileStore.getLocalTempFile(). 
            If userPath is specified and this is not true a RuntimeError exception 
            will be raised. If userPath is specified and the file is already cached, 
            the userPath file will be a hard link to the actual location, else it 
            will be an actual copy of the file.  
            """
            if fileStoreID in self.filesToDelete:
                raise RuntimeError("Trying to access a file in the jobStore you've deleted: %s" % fileStoreID)
            if userPath != None:
                userPath = os.path.abspath(userPath) #Make an absolute path
                #Check it is a valid location
                if not userPath.startswith(self.localTempDir):
                    raise RuntimeError("The user path is not contained within the"
                                       " temporary file hierarchy created by the job."
                                       " User path: %s, temporary file root path: %s" % 
                                       (userPath, self.localTempDir))
            #When requesting a new file from the jobStore first check if fileStoreID
            #is a key in jobStoreFileIDToCacheLocation.
            if fileStoreID in self.jobStoreFileIDToCacheLocation:
                cachedAbsFilePath = self.jobStoreFileIDToCacheLocation[fileStoreID]   
                #If the user specifies a location and it is not the current location
                # return a hardlink to the location, else return the original location
                if userPath == None or userPath == cachedAbsFilePath:
                    return cachedAbsFilePath
                if os.path.exists(userPath):
                    os.remove(userPath)
                os.link(cachedAbsFilePath, userPath)
                return userPath
            else:
                #If it is not in the cache read it from the jobStore to the 
                #desired location
                localFilePath = userPath if userPath != None else self.getLocalTempFile()
                self.jobStore.readFile(fileStoreID, localFilePath)
                self.jobStoreFileIDToCacheLocation[fileStoreID] = localFilePath
                #Chmod to make file read only
                os.chmod(localFilePath, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
                return localFilePath