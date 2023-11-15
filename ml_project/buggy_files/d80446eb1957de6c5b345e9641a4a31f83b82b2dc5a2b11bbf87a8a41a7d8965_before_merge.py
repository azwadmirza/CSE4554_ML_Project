    def getIssuedBatchJobIDs(self):
        """
        A list of jobs (as jobIDs) currently issued (may be running, or maybe just waiting).
        """
        # TODO: Ensure jobList holds jobs that have been "launched" from Mesos
        jobList = []
        for k, queue in self.jobQueueList.iteritems():
            for item in queue:
                jobList.append(item.jobID)
        for k, v in self.runningJobMap.iteritems():
            jobList.append(k)

        return jobList