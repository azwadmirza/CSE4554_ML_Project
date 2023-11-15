    def processFinishedJob(self, jobBatchSystemID, resultStatus, wallTime=None):
        """
        Function reads a processed jobWrapper file and updates it state.
        """
        def processRemovedJob(jobStoreID):
            if resultStatus != 0:
                logger.warn("Despite the batch system claiming failure the "
                            "jobWrapper %s seems to have finished and been removed", jobStoreID)
            self._updatePredecessorStatus(jobStoreID)

        if wallTime is not None and self.clusterScaler is not None:
            issuedJob = self.jobBatchSystemIDToIssuedJob[jobBatchSystemID]
            self.clusterScaler.addCompletedJob(issuedJob, wallTime)
        jobStoreID = self.removeJobID(jobBatchSystemID)
        if self.jobStore.exists(jobStoreID):
            logger.debug("Job %s continues to exist (i.e. has more to do)" % jobStoreID)
            try:
                jobWrapper = self.jobStore.load(jobStoreID)
            except NoSuchJobException:
                if isinstance(self.jobStore, AWSJobStore):
                    # We have a ghost job - the job has been deleted but a stale read from
                    # SDB gave us a false positive when we checked for its existence.
                    # Process the job from here as any other job removed from the job store.
                    # This is a temporary work around until https://github.com/BD2KGenomics/toil/issues/1091
                    # is completed
                    logger.warn('Got a stale read from SDB for job %s', jobStoreID)
                    processRemovedJob(jobStoreID)
                    return
                else:
                    raise
            if jobWrapper.logJobStoreFileID is not None:
                logger.warn("The jobWrapper seems to have left a log file, indicating failure: %s", jobStoreID)
                with jobWrapper.getLogFileHandle( self.jobStore ) as logFileStream:
                    logStream( logFileStream, jobStoreID, logger.warn )
            if resultStatus != 0:
                # If the batch system returned a non-zero exit code then the worker
                # is assumed not to have captured the failure of the job, so we
                # reduce the retry count here.
                if jobWrapper.logJobStoreFileID is None:
                    logger.warn("No log file is present, despite jobWrapper failing: %s", jobStoreID)
                jobWrapper.setupJobAfterFailure(self.config)
                self.jobStore.update(jobWrapper)
            elif jobStoreID in self.toilState.hasFailedSuccessors:
                # If the job has completed okay, we can remove it from the list of jobs with failed successors
                self.toilState.hasFailedSuccessors.remove(jobStoreID)

            self.toilState.updatedJobs.add((jobWrapper, resultStatus)) #Now we know the
            #jobWrapper is done we can add it to the list of updated jobWrapper files
            logger.debug("Added jobWrapper: %s to active jobs", jobStoreID)
        else:  #The jobWrapper is done
            processRemovedJob(jobStoreID)