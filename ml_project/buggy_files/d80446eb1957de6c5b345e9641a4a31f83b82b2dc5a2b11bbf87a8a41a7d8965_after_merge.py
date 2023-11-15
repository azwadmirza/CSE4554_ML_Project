    def getIssuedBatchJobIDs(self):
        """
        A list of jobs (as jobIDs) currently issued (may be running, or maybe just waiting).
        """
        # TODO: Ensure jobList holds jobs that have been "launched" from Mesos
        jobList = set()
        for queue in self.jobQueueList.values():
            for item in queue:
                jobList.add(item.jobID)
        for key in self.runningJobMap.keys():
            jobList.add(key)

        return list(jobList)