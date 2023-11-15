    def processTotallyFailedJob(self, jobWrapper):
        """
        Processes a totally failed job.
        """
        # Mark job as a totally failed job
        self.toilState.totalFailedJobs.add(jobWrapper.jobStoreID)

        if jobWrapper.jobStoreID in self.toilState.serviceJobStoreIDToPredecessorJob: # Is
            # a service job
            logger.debug("Service job is being processed as a totally failed job: %s" % jobWrapper.jobStoreID)

            predecessorJobWrapper = self.toilState.serviceJobStoreIDToPredecessorJob[jobWrapper.jobStoreID]

            # This removes the service job as a service of the predecessor
            # and potentially makes the predecessor active
            self._updatePredecessorStatus(jobWrapper.jobStoreID)

            # Remove the start flag, if it still exists. This indicates
            # to the service manager that the job has "started", this prevents
            # the service manager from deadlocking while waiting
            self.jobStore.deleteFile(jobWrapper.startJobStoreID)

            # Signal to any other services in the group that they should
            # terminate. We do this to prevent other services in the set
            # of services from deadlocking waiting for this service to start properly
            if predecessorJobWrapper.jobStoreID in self.toilState.servicesIssued:
                self.serviceManager.killServices(self.toilState.servicesIssued[predecessorJobWrapper.jobStoreID], error=True)
                logger.debug("Job: %s is instructing all the services of its parent job to quit", jobWrapper.jobStoreID)

            self.toilState.hasFailedSuccessors.add(predecessorJobWrapper.jobStoreID) # This ensures that the
            # job will not attempt to run any of it's successors on the stack
        else:
            # Is a non-service job
            assert jobWrapper.jobStoreID not in self.toilState.servicesIssued
            
            # Traverse failed job's successor graph and get the jobStoreID of new successors.
            # Any successor already in toilState.failedSuccessors will not be traversed
            # All successors traversed will be added to toilState.failedSuccessors and returned
            # as a set (unseenSuccessors).
            unseenSuccessors = self.getSuccessors(jobWrapper, self.toilState.failedSuccessors, self.jobStore)
            logger.debug("Found new failed successors: %s of job: %s" % (" ".join(unseenSuccessors), jobWrapper.jobStoreID))
            
            # For each newly found successor
            for successorJobStoreID in unseenSuccessors:
                
                # If the successor is a successor of other jobs that have already tried to schedule it
                if successorJobStoreID in self.toilState.successorJobStoreIDToPredecessorJobs:
                    
                    # For each such predecessor job
                    # (we remove the successor from toilState.successorJobStoreIDToPredecessorJobs to avoid doing 
                    # this multiple times for each failed predecessor)
                    for predecessorJob in self.toilState.successorJobStoreIDToPredecessorJobs.pop(successorJobStoreID):
                        
                        # Reduce the predecessor job's successor count.
                        self.toilState.successorCounts[predecessorJob.jobStoreID] -= 1
                        
                        # Indicate that it has failed jobs.  
                        self.toilState.hasFailedSuccessors.add(predecessorJob.jobStoreID)
                        logger.debug("Marking job: %s as having failed successors (found by reading successors failed job)" % predecessorJob.jobStoreID)
                        
                        # If the predecessor has no remaining successors, add to list of active jobs
                        assert self.toilState.successorCounts[predecessorJob.jobStoreID] >= 0
                        if self.toilState.successorCounts[predecessorJob.jobStoreID] == 0:
                            self.toilState.updatedJobs.add((predecessorJob, 0))
                            
                            # Remove the predecessor job from the set of jobs with successors. 
                            self.toilState.successorCounts.pop(predecessorJob.jobStoreID) 

            # If the job has predecessor(s)
            if jobWrapper.jobStoreID in self.toilState.successorJobStoreIDToPredecessorJobs:
                
                # For each predecessor of the job
                for predecessorJobWrapper in self.toilState.successorJobStoreIDToPredecessorJobs[jobWrapper.jobStoreID]:
                    
                    # Mark the predecessor as failed
                    self.toilState.hasFailedSuccessors.add(predecessorJobWrapper.jobStoreID)
                    logger.debug("Totally failed job: %s is marking direct predecessor: %s as having failed jobs", jobWrapper.jobStoreID, predecessorJobWrapper.jobStoreID)

                self._updatePredecessorStatus(jobWrapper.jobStoreID)