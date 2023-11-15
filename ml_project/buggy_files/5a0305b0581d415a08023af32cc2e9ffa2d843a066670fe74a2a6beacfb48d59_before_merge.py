    def clean(self, jobCache=None):
        """
        Function to cleanup the state of a job store after a restart.
        Fixes jobs that might have been partially updated. Resets the try counts and removes jobs
        that are not successors of the current root job.

        :param dict[str,toil.jobWrapper.JobWrapper] jobCache: if a value it must be a dict
               from job ID keys to JobWrapper object values. Jobs will be loaded from the cache
               (which can be downloaded from the job store in a batch) instead of piecemeal when 
               recursed into.
        """
        if jobCache is None:
            logger.warning("Cleaning jobStore recursively. This may be slow.")
        
        # Functions to get and check the existence of jobs, using the jobCache
        # if present
        def getJob(jobId):
            if jobCache is not None:
                try:
                    return jobCache[jobId]
                except KeyError:
                    self.load(jobId)
            else:
                return self.load(jobId)

        def haveJob(jobId):
            if jobCache is not None:
                if jobCache.has_key(jobId):
                    return True
                else:
                    return self.exists(jobId)
            else:
                return self.exists(jobId)

        def getJobs():
            if jobCache is not None:
                return jobCache.itervalues()
            else:
                return self.jobs()
        
        # Iterate from the root jobWrapper and collate all jobs that are reachable from it
        # All other jobs returned by self.jobs() are orphaned and can be removed
        reachableFromRoot = set()

        def getConnectedJobs(jobWrapper):
            if jobWrapper.jobStoreID in reachableFromRoot:
                return
            reachableFromRoot.add(jobWrapper.jobStoreID)
            # Traverse jobs in stack
            for jobs in jobWrapper.stack:
                for successorJobStoreID in map(lambda x: x[0], jobs):
                    if successorJobStoreID not in reachableFromRoot and haveJob(successorJobStoreID):
                        getConnectedJobs(getJob(successorJobStoreID))
            # Traverse service jobs
            for jobs in jobWrapper.services:
                for serviceJobStoreID in map(lambda x: x[0], jobs):
                    if haveJob(serviceJobStoreID):
                        assert serviceJobStoreID not in reachableFromRoot
                        reachableFromRoot.add(serviceJobStoreID)

        logger.info("Checking job graph connectivity...")
        getConnectedJobs(self.loadRootJob())
        logger.info("%d jobs reachable from root." % len(reachableFromRoot))

        # Cleanup jobs that are not reachable from the root, and therefore orphaned
        jobsToDelete = filter(lambda x : x.jobStoreID not in reachableFromRoot, getJobs())
        for jobWrapper in jobsToDelete:
            # clean up any associated files before deletion
            for fileID in jobWrapper.filesToDelete:
                # Delete any files that should already be deleted
                logger.critical(
                    "Removing file in job store: %s that was marked for deletion but not previously removed" % fileID)
                self.deleteFile(fileID)
            # Delete the job
            self.delete(jobWrapper.jobStoreID)

        # Clean up jobs that are in reachable from the root
        for jobWrapper in (getJob(x) for x in reachableFromRoot):
            # jobWrappers here are necessarily in reachable from root.
            
            changed = [False] # This is a flag to indicate the jobWrapper state has 
            # changed
            
            # If the job has files to delete delete them.
            if len(jobWrapper.filesToDelete) != 0:
                # Delete any files that should already be deleted
                for fileID in jobWrapper.filesToDelete:
                    logger.critical("Removing file in job store: %s that was "
                                    "marked for deletion but not previously removed" % fileID)
                    self.deleteFile(fileID)
                jobWrapper.filesToDelete = []
                changed[0] = True

            # For a job whose command is already executed, remove jobs from the
            # stack that are already deleted. 
            # This cleans up the case that the jobWrapper
            # had successors to run, but had not been updated to reflect this
            if jobWrapper.command is None:
                stackSizeFn = lambda : sum(map(len, jobWrapper.stack))
                startStackSize = stackSizeFn()
                # Remove deleted jobs
                jobWrapper.stack = map(lambda x : filter(lambda y : self.exists(y[0]), x), jobWrapper.stack)
                # Remove empty stuff from the stack
                jobWrapper.stack = filter(lambda x : len(x) > 0, jobWrapper.stack)
                # Check if anything got removed
                if stackSizeFn() != startStackSize:
                    changed[0] = True
                
            # Cleanup any services that have already been finished.
            # Filter out deleted services and update the flags for services that exist
            # If there are services then renew  
            # the start and terminate flags if they have been removed
            def subFlagFile(jobStoreID, jobStoreFileID, flag):
                if self.fileExists(jobStoreFileID):
                    return jobStoreFileID
                
                # Make a new flag
                newFlag = self.getEmptyFileStoreID()
                
                # Load the jobWrapper for the service and initialise the link
                serviceJobWrapper = getJob(jobStoreID)
                
                if flag == 1:
                    logger.debug("Recreating a start service flag for job: %s, flag: %s", jobStoreID, newFlag)
                    serviceJobWrapper.startJobStoreID = newFlag
                elif flag == 2:
                    logger.debug("Recreating a terminate service flag for job: %s, flag: %s", jobStoreID, newFlag)
                    serviceJobWrapper.terminateJobStoreID = newFlag
                else:
                    logger.debug("Recreating a error service flag for job: %s, flag: %s", jobStoreID, newFlag)
                    assert flag == 3
                    serviceJobWrapper.errorJobStoreID = newFlag
                    
                # Update the service job on disk
                self.update(serviceJobWrapper)
                
                changed[0] = True
                
                return newFlag
            
            servicesSizeFn = lambda : sum(map(len, jobWrapper.services))
            startServicesSize = servicesSizeFn()
            jobWrapper.services = filter(lambda z : len(z) > 0, map(lambda serviceJobList : 
                                        map(lambda x : x[:4] + (subFlagFile(x[0], x[4], 1), 
                                                                subFlagFile(x[0], x[5], 2), 
                                                                subFlagFile(x[0], x[6], 3)), 
                                        filter(lambda y : self.exists(y[0]), serviceJobList)), jobWrapper.services)) 
            if servicesSizeFn() != startServicesSize:
                changed[0] = True

            # Reset the retry count of the jobWrapper
            if jobWrapper.remainingRetryCount != self._defaultTryCount():
                jobWrapper.remainingRetryCount = self._defaultTryCount()
                changed[0] = True

            # This cleans the old log file which may
            # have been left if the jobWrapper is being retried after a jobWrapper failure.
            if jobWrapper.logJobStoreFileID != None:
                self.delete(jobWrapper.logJobStoreFileID)
                jobWrapper.logJobStoreFileID = None
                changed[0] = True

            if changed[0]:  # Update, but only if a change has occurred
                logger.critical("Repairing job: %s" % jobWrapper.jobStoreID)
                self.update(jobWrapper)

        # Remove any crufty stats/logging files from the previous run
        logger.info("Discarding old statistics and logs...")
        self.readStatsAndLogging(lambda x: None)

        logger.info("Job store is clean")
        # TODO: reloading of the rootJob may be redundant here
        return self.loadRootJob()