    def _serialiseJob(self, jobStore, jobsToJobWrappers, rootJobWrapper):
        """
        Pickle a job and its jobWrapper to disk.
        """
        #Pickle the job so that its run method can be run at a later time.
        #Drop out the children/followOns/predecessors/services - which are
        #all recorded within the jobStore and do not need to be stored within
        #the job
        self._children = []
        self._followOns = []
        self._services = []
        self._directPredecessors = set()
        #The pickled job is "run" as the command of the job, see worker
        #for the mechanism which unpickles the job and executes the Job.run
        #method.
        with jobStore.writeFileStream(rootJobWrapper.jobStoreID) as (fileHandle, fileStoreID):
            cPickle.dump(self, fileHandle, cPickle.HIGHEST_PROTOCOL)
        jobsToJobWrappers[self].command = ' '.join( ('_toil', fileStoreID) + self.userModule.globalize())
        #Update the status of the jobWrapper on disk
        jobStore.update(jobsToJobWrappers[self])