    def clean(self, rootJobWrapper):
        """
        Function to cleanup the state of a jobStore after a restart.
        Fixes jobs that might have been partially updated.
        Resets the try counts.
        Removes jobs that are not successors of the rootJobWrapper. 
        """
        #Iterate from the root jobWrapper and collate all jobs that are reachable from it
        #All other jobs returned by self.jobs() are orphaned and can be removed
        reachableFromRoot = set()
        def getConnectedJobs(jobWrapper):
            if jobWrapper.jobStoreID in reachableFromRoot:
                return
            reachableFromRoot.add(jobWrapper.jobStoreID)
            for jobs in jobWrapper.stack:
                for successorJobStoreID in map(lambda x : x[0], jobs):
                    if successorJobStoreID not in reachableFromRoot and self.exists(successorJobStoreID):
                        getConnectedJobs(self.load(successorJobStoreID))
        getConnectedJobs(rootJobWrapper)
        
        #Cleanup the state of each jobWrapper
        for jobWrapper in self.jobs():
            changed = False #Flag to indicate if we need to update the jobWrapper
            #on disk
            
            if len(jobWrapper.filesToDelete) != 0:
                #Delete any files that should already be deleted
                for fileID in jobWrapper.filesToDelete:
                    logger.critical("Removing file in job store: %s that was marked for deletion but not previously removed" % fileID)
                    self.deleteFile(fileID)
                jobWrapper.filesToDelete = set()
                changed = True
            
            #Delete a jobWrapper if it is not reachable from the rootJobWrapper
            if jobWrapper.jobStoreID not in reachableFromRoot:
                logger.critical("Removing job: %s that is not a successor of the root job in cleanup" % jobWrapper.jobStoreID)
                self.delete(jobWrapper.jobStoreID)
                continue
                
            #While jobs at the end of the stack are already deleted remove
            #those jobs from the stack (this cleans up the case that the jobWrapper
            #had successors to run, but had not been updated to reflect this)
            while len(jobWrapper.stack) > 0:
                jobs = [ command for command in jobWrapper.stack[-1] if self.exists(command[0]) ]
                if len(jobs) < len(jobWrapper.stack[-1]):
                    changed = True
                    if len(jobs) > 0:
                        jobWrapper.stack[-1] = jobs
                        break
                    else:
                        jobWrapper.stack.pop()
                else:
                    break
                          
            #Reset the retry count of the jobWrapper 
            if jobWrapper.remainingRetryCount != self._defaultTryCount():
                jobWrapper.remainingRetryCount = self._defaultTryCount()
                changed = True
                          
            #This cleans the old log file which may 
            #have been left if the jobWrapper is being retried after a jobWrapper failure.
            if jobWrapper.logJobStoreFileID != None:
                self.delete(jobWrapper.logJobStoreFileID)
                jobWrapper.logJobStoreFileID = None
                changed = True
            
            if changed: #Update, but only if a change has occurred
                self.update(jobWrapper)
        
        #Remove any crufty stats/logging files from the previous run
        self.readStatsAndLogging(lambda x : None)