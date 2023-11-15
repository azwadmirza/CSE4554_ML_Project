    def _buildToilState(self, jobWrapper, jobStore, jobCache=None):
        """
        Traverses tree of jobs from the root jobWrapper (rootJob) building the
        ToilState class.

        If jobCache is passed, it must be a dict from job ID to JobWrapper
        object. Jobs will be loaded from the cache (which can be downloaded from
        the jobStore in a batch) instead of piecemeal when recursed into.
        """

        def getJob(jobId):
            if jobCache is not None:
                try:
                    return jobCache[jobId]
                except ValueError:
                    return jobStore.load(jobId)
            else:
                return jobStore.load(jobId)

        # If the jobWrapper has a command, is a checkpoint, has services or is ready to be
        # deleted it is ready to be processed
        if (jobWrapper.command is not None
            or jobWrapper.checkpoint is not None
            or len(jobWrapper.services) > 0
            or len(jobWrapper.stack) == 0):
            logger.debug('Found job to run: %s, with command: %s, with checkpoint: %s, '
                         'with  services: %s, with stack: %s', jobWrapper.jobStoreID,
                         jobWrapper.command is not None, jobWrapper.checkpoint is not None,
                         len(jobWrapper.services) > 0, len(jobWrapper.stack) == 0)
            self.updatedJobs.add((jobWrapper, 0))

            if jobWrapper.checkpoint is not None:
                jobWrapper.command = jobWrapper.checkpoint

        else: # There exist successors
            logger.debug("Adding job: %s to the state with %s successors" % (jobWrapper.jobStoreID, len(jobWrapper.stack[-1])))
            
            # Record the number of successors
            self.successorCounts[jobWrapper.jobStoreID] = len(jobWrapper.stack[-1])
            
            def processSuccessorWithMultiplePredecessors(successorJobWrapper):
                # If jobWrapper job is not reported as complete by the successor
                if jobWrapper.jobStoreID not in successorJobWrapper.predecessorsFinished:
                    
                    # Update the sucessor's status to mark the predecessor complete
                    successorJobWrapper.predecessorsFinished.add(jobWrapper.jobStoreID)
            
                # If the successor has no predecessors to finish
                assert len(successorJobWrapper.predecessorsFinished) <= successorJobWrapper.predecessorNumber
                if len(successorJobWrapper.predecessorsFinished) == successorJobWrapper.predecessorNumber:
                    
                    # It is ready to be run, so remove it from the cache
                    self.jobsToBeScheduledWithMultiplePredecessors.pop(successorJobStoreID)
                    
                    # Recursively consider the successor
                    self._buildToilState(successorJobWrapper, jobStore, jobCache=jobCache)
            
            # For each successor
            for successorJobStoreTuple in jobWrapper.stack[-1]:
                successorJobStoreID = successorJobStoreTuple[0]
                
                # If the successor jobWrapper does not yet point back at a
                # predecessor we have not yet considered it
                if successorJobStoreID not in self.successorJobStoreIDToPredecessorJobs:

                    # Add the job as a predecessor
                    self.successorJobStoreIDToPredecessorJobs[successorJobStoreID] = [jobWrapper]
                    
                    # If predecessorJobStoreID is not None then the successor has multiple predecessors
                    predecessorJobStoreID = successorJobStoreTuple[-1]
                    if predecessorJobStoreID != None: 
                        
                        # We load the successor job
                        successorJobWrapper =  getJob(successorJobStoreID)
                        
                        # We put the successor job in the cache of successor jobs with multiple predecessors
                        assert successorJobStoreID not in self.jobsToBeScheduledWithMultiplePredecessors
                        self.jobsToBeScheduledWithMultiplePredecessors[successorJobStoreID] = successorJobWrapper
                        
                        # Process successor
                        processSuccessorWithMultiplePredecessors(successorJobWrapper)
                            
                    else:
                        # The successor has only the jobWrapper job as a predecessor so
                        # recursively consider the successor
                        self._buildToilState(getJob(successorJobStoreID), jobStore, jobCache=jobCache)
                
                else:
                    # We've already seen the successor
                    
                    # Add the job as a predecessor
                    assert jobWrapper not in self.successorJobStoreIDToPredecessorJobs[successorJobStoreID]
                    self.successorJobStoreIDToPredecessorJobs[successorJobStoreID].append(jobWrapper) 
                    
                    # If the successor has multiple predecessors
                    if successorJobStoreID in self.jobsToBeScheduledWithMultiplePredecessors:
                        
                        # Get the successor from cache
                        successorJobWrapper = self.jobsToBeScheduledWithMultiplePredecessors[successorJobStoreID]
                        
                        # Process successor
                        processSuccessorWithMultiplePredecessors(successorJobWrapper)