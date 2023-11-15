        def __init__(self, jobStore, jobWrapper, localTempDir, 
                     inputBlockFn, jobStoreFileIDToCacheLocation, terminateEvent):
            """
            This constructor should not be called by the user, 
            FileStore instances are only provided as arguments 
            to the run function.
            """
            self.jobStore = jobStore
            self.jobWrapper = jobWrapper
            self.localTempDir = os.path.abspath(localTempDir)
            self.loggingMessages = []
            self.filesToDelete = set()
            self.jobsToDelete = set()
            #Asynchronous writes stuff
            self.workerNumber = 2
            self.queue = Queue()
            self.updateSemaphore = Semaphore() 
            self.terminateEvent = terminateEvent
            #Function to write files to job store
            def asyncWrite():
                try:
                    while True:
                        try:
                            #Block for up to two seconds waiting for a file
                            args = self.queue.get(timeout=2)
                        except Empty:
                            #Check if termination event is signaled 
                            #(set in the event of an exception in the worker)
                            if terminateEvent.isSet():
                                raise RuntimeError("The termination flag is set, exiting")
                            continue
                        #Normal termination condition is getting None from queue
                        if args == None:
                            break
                        inputFileHandle, jobStoreFileID = args
                        #We pass in a fileHandle, rather than the file-name, in case 
                        #the file itself is deleted. The fileHandle itself should persist 
                        #while we maintain the open file handle
                        with jobStore.updateFileStream(jobStoreFileID) as outputFileHandle:
                            bufferSize=1000000 #TODO: This buffer number probably needs to be modified/tuned
                            while 1:
                                copyBuffer = inputFileHandle.read(bufferSize)
                                if not copyBuffer:
                                    break
                                outputFileHandle.write(copyBuffer)
                        inputFileHandle.close()
                except:
                    terminateEvent.set()
                    raise
                    
            self.workers = map(lambda i : Thread(target=asyncWrite), 
                               range(self.workerNumber))
            for worker in self.workers:
                worker.start()
            self.inputBlockFn = inputBlockFn
            #Caching 
            #
            #For files in jobStore that are on the local disk, 
            #map of jobStoreFileIDs to locations in localTempDir.
            self.jobStoreFileIDToCacheLocation = jobStoreFileIDToCacheLocation