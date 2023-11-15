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
            self.successorCounts[jobWrapper.jobStoreID] = len(jobWrapper.stack[-1])
            for successorJobStoreTuple in jobWrapper.stack[-1]:
                successorJobStoreID = successorJobStoreTuple[0]
                if successorJobStoreID not in self.successorJobStoreIDToPredecessorJobs:
                    #Given that the successor jobWrapper does not yet point back at a
                    #predecessor we have not yet considered it, so we call the function
                    #on the successor
                    self.successorJobStoreIDToPredecessorJobs[successorJobStoreID] = [jobWrapper]
                    self._buildToilState(getJob(successorJobStoreID), jobStore, jobCache=jobCache)
                else:
                    #We have already looked at the successor, so we don't recurse,
                    #but we add back a predecessor link
                    self.successorJobStoreIDToPredecessorJobs[successorJobStoreID].append(jobWrapper)