        def readGlobalFile(self, fileStoreID, userPath=None, cache=True):
            """
            Returns an absolute path to a local, temporary copy of the file 
            keyed by fileStoreID. 
            
            :param userPath: a path to the name of file to which the global file will be 
            copied or hard-linked (see below). 
            
            :param cache: a boolean to switch on caching (see below). Caching will 
            attempt to keep copies of files between sequences of jobs run on the same 
            worker. 
            
            If cache=True and userPath is either: 
            (1) a file path contained within a directory or, 
            recursively, a subdirectory of a temporary directory returned by 
            Job.FileStore.getLocalTempDir(), or (2) a file path returned by 
            Job.FileStore.getLocalTempFile() then the file will be cached and
            returned file will be read only (have permissions 444).
            If userPath is specified and the file is already cached, 
            the userPath file will be a hard link to the actual location, else it 
            will be an actual copy of the file. 
            
            If the cache=False or userPath is not either of the above the file 
            will not be cached and will have default permissions. Note, if the file
            is already cached this will result in two copies of the file on the system.
            
            :rtype : the absolute path to the read file
            """
            if fileStoreID in self.filesToDelete:
                raise RuntimeError("Trying to access a file in the jobStore you've deleted: %s" % fileStoreID)
            if userPath != None:
                userPath = os.path.abspath(userPath) #Make an absolute path
                #Turn off caching if user file is not in localTempDir
                if cache and not userPath.startswith(self.localTempDir):
                    cache = False  
            #When requesting a new file from the jobStore first check if fileStoreID
            #is a key in jobStoreFileIDToCacheLocation.
            if fileStoreID in self.jobStoreFileIDToCacheLocation:
                cachedAbsFilePath = self.jobStoreFileIDToCacheLocation[fileStoreID]   
                if cache:
                    #If the user specifies a location and it is not the current location
                    #return a hardlink to the location, else return the original location
                    if userPath == None or userPath == cachedAbsFilePath:
                        return cachedAbsFilePath
                    #Chmod to make file read only
                    if os.path.exists(userPath):
                        os.remove(userPath)
                    os.link(cachedAbsFilePath, userPath)
                    return userPath
                else:
                    #If caching is not true then make a copy of the file
                    localFilePath = userPath if userPath != None else self.getLocalTempFile()
                    shutil.copyfile(cachedAbsFilePath, localFilePath)
                    return localFilePath
            else:
                #If it is not in the cache read it from the jobStore to the 
                #desired location
                localFilePath = userPath if userPath != None else self.getLocalTempFile()
                self.jobStore.readFile(fileStoreID, localFilePath)
                #If caching is enabled and the file is in local temp dir then
                #add to cache and make read only
                if cache:
                    assert localFilePath.startswith(self.localTempDir)
                    self.jobStoreFileIDToCacheLocation[fileStoreID] = localFilePath
                    os.chmod(localFilePath, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
                return localFilePath