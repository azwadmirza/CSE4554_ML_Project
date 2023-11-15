    def _updatePredecessorStatus(self, jobStoreID):
        """
        Update status of a predecessor for finished successor job.
        """
        if jobStoreID in self.toilState.serviceJobStoreIDToPredecessorJob:
            # Is a service job
            predecessorJob = self.toilState.serviceJobStoreIDToPredecessorJob.pop(jobStoreID)
            self.toilState.servicesIssued[predecessorJob.jobStoreID].pop(jobStoreID)
            if len(self.toilState.servicesIssued[predecessorJob.jobStoreID]) == 0: # Predecessor job has
                # all its services terminated
                self.toilState.servicesIssued.pop(predecessorJob.jobStoreID) # The job has no running services
                self.toilState.updatedJobs.add((predecessorJob, 0)) # Now we know
                # the job is done we can add it to the list of updated job files
                logger.debug("Job %s services have completed or totally failed, adding to updated jobs" % predecessorJob.jobStoreID)

        elif jobStoreID not in self.toilState.successorJobStoreIDToPredecessorJobs:
            #We have reach the root job
            assert len(self.toilState.updatedJobs) == 0
            assert len(self.toilState.successorJobStoreIDToPredecessorJobs) == 0
            assert len(self.toilState.successorCounts) == 0

        else:
            for predecessorJob in self.toilState.successorJobStoreIDToPredecessorJobs.pop(jobStoreID):
                self.toilState.successorCounts[predecessorJob.jobStoreID] -= 1
                assert self.toilState.successorCounts[predecessorJob.jobStoreID] >= 0
                if self.toilState.successorCounts[predecessorJob.jobStoreID] == 0: #Job is done
                    self.toilState.successorCounts.pop(predecessorJob.jobStoreID)
                    predecessorJob.stack.pop()
                    logger.debug('Job %s has all its non-service successors completed or totally '
                                 'failed', predecessorJob.jobStoreID)
                    assert predecessorJob not in self.toilState.updatedJobs
                    self.toilState.updatedJobs.add((predecessorJob, 0)) #Now we know