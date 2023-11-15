    def _deleteByJobID(self, jobID, ):
        # FIXME: not efficient, I'm sure.
        for key, jobType in self.jobQueueList.iteritems():
            for job in jobType:
                if jobID == job.jobID:
                    jobType.remove(job)