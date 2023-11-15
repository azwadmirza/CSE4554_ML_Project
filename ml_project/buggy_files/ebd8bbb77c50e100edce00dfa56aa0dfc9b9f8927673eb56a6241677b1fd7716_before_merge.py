    def __enter__(self):
        """
        Derive configuration from the command line options, load the job store and, on restart,
        consolidate the derived configuration with the one from the previous invocation of the
        workflow.
        """
        setLoggingFromOptions(self.options)
        self._inContextManager = True
        self.config = Config()
        self.config.setOptions(self.options)
        self._jobStore = self.loadOrCreateJobStore(self.config.jobStore,
                                                   config=None if self.config.restart else self.config)
        if self.config.restart:
            # Reload configuration from job store
            self.config = self._jobStore.config
            self.config.setOptions(self.options)
            self.config.workflowAttemptNumber += 1
            self._jobStore.writeConfigToStore()

        return self