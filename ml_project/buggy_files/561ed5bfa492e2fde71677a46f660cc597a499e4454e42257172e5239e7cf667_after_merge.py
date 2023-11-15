    def _deleteByJobID(self, jobID, ):
        # FIXME: not efficient, I'm sure.
        for jobType in self.jobQueueList.values():
            for job in jobType:
                if jobID == job.jobID:
                    jobType.remove(job)