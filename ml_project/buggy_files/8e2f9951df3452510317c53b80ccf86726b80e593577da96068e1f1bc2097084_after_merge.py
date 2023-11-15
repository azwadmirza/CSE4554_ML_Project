        def _updateJobWhenDone(self):
            """
            Asynchronously update the status of the job on the disk, first waiting
            until the writing threads have finished and the inputBlockFn has stopped
            blocking.
            """
            def asyncUpdate():
                try:
                    #Wait till all file writes have completed
                    for i in xrange(len(self.workers)):
                        self.queue.put(None)
            
                    for thread in self.workers:
                        thread.join()
                    
                    #Wait till input block-fn returns - in the event of an exception
                    #this will eventually terminate 
                    self.inputBlockFn()
                    
                    #Check the terminate event, if set we can not guarantee
                    #that the workers ended correctly, therefore we exit without
                    #completing the update
                    if self.terminateEvent.isSet():
                        raise RuntimeError("The termination flag is set, exiting before update")
                    
                    #Indicate any files that should be deleted once the update of 
                    #the job wrapper is completed.
                    self.jobWrapper.filesToDelete = list(self.filesToDelete)
                    
                    #Complete the job
                    self.jobStore.update(self.jobWrapper)
                    
                    #Delete any remnant jobs
                    map(self.jobStore.delete, self.jobsToDelete)
                    
                    #Delete any remnant files
                    map(self.jobStore.deleteFile, self.filesToDelete)
                    
                    #Remove the files to delete list, having successfully removed the files
                    if len(self.filesToDelete) > 0:
                        self.jobWrapper.filesToDelete = []
                        #Update, removing emptying files to delete
                        self.jobStore.update(self.jobWrapper)
                except:
                    self.terminateEvent.set()
                    raise
                finally:
                    #Indicate that _blockFn can return
                    #This code will always run
                    self.updateSemaphore.release()
            #The update semaphore is held while the jobWrapper is written to disk
            try:
                self.updateSemaphore.acquire()
                t = Thread(target=asyncUpdate)
                t.start()
            except: #This is to ensure that the semaphore is released in a crash to stop a deadlock scenario
                self.updateSemaphore.release()
                raise