    def start(self, rootJob):
        """
        Invoke a Toil workflow with the given job as the root for an initial run. This method
        must be called in the body of a ``with Toil(...) as toil:`` statement. This method should
        not be called more than once for a workflow that has not finished.

        :param toil.job.Job rootJob: The root job of the workflow
        :return: The root job's return value
        """
        self._assertContextManagerUsed()
        if self.config.restart:
            raise ToilRestartException('A Toil workflow can only be started once. Use '
                                       'Toil.restart() to resume it.')

        self._batchSystem = self.createBatchSystem(self.config)
        self._setupHotDeployment(rootJob.getUserScript())
        try:
            self._setBatchSystemEnvVars()
            self._serialiseEnv()
            self._cacheAllJobs()

            # Make a file to store the root job's return value in
            rootJobReturnValueID = self._jobStore.getEmptyFileStoreID()

            # Add the root job return value as a promise
            rootJob._rvs[()].append(rootJobReturnValueID)

            # Write the name of the promise file in a shared file
            with self._jobStore.writeSharedFileStream("rootJobReturnValue") as fH:
                fH.write(rootJobReturnValueID)

            # Setup the first wrapper and cache it
            job = rootJob._serialiseFirstJob(self._jobStore)
            self._cacheJob(job)

            self._setProvisioner()
            return self._runMainLoop(job)
        finally:
            self._shutdownBatchSystem()