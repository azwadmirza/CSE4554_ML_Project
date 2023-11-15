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
            assert jobWrapper.jobStoreID not in self.toilState.servicesIssued

            # Is a non-service job, walk up the tree killing services of any jobs with nothing left to do.
            if jobWrapper.jobStoreID in self.toilState.successorJobStoreIDToPredecessorJobs:
                for predecessorJobWrapper in self.toilState.successorJobStoreIDToPredecessorJobs[jobWrapper.jobStoreID]:
                    self.toilState.hasFailedSuccessors.add(predecessorJobWrapper.jobStoreID)
                    logger.debug("Totally failed job: %s is marking direct predecessors %s as having failed jobs", jobWrapper.jobStoreID, predecessorJobWrapper.jobStoreID)
                self._updatePredecessorStatus(jobWrapper.jobStoreID)