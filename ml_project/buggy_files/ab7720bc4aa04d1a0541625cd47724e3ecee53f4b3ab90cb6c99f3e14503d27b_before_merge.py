    def restart(self):
        """
        Restarts a workflow that has been interrupted. This method should be called if and only
        if a workflow has previously been started and has not finished.

        :return: The root job's return value
        """
        self._assertContextManagerUsed()
        if not self.config.restart:
            raise ToilRestartException('A Toil workflow must be initiated with Toil.start(), '
                                       'not restart().')

        self._batchSystem = self.createBatchSystem(self.config, jobStore=self._jobStore)
        try:
            self._setBatchSystemEnvVars()
            self._serialiseEnv()
            self._cacheAllJobs()
            self._setProvisioner()
            rootJob = self._jobStore.clean(jobCache=self._jobCache)
            return self._runMainLoop(rootJob)
        finally:
            self._shutdownBatchSystem()