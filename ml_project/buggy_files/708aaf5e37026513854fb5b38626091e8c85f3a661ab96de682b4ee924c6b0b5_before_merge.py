    def getRunningBatchJobIDs(self):
        """
        Gets a map of jobs (as jobIDs) currently running (not just waiting) and a how long they have been running for
        (in seconds).
        """
        currentTime = dict()
        for jobID, data in self.runningJobMap.iteritems():
            currentTime[jobID] = time.time() - data.startTime
        return currentTime