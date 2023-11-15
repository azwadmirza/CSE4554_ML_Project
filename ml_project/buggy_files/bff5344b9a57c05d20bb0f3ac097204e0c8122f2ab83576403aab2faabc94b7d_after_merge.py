    def _createEmptyJobForJob(self, jobStore, command=None, predecessorNumber=0):
        """
        Create an empty job for the job.
        """
        requirements = self.effectiveRequirements(jobStore.config)
        del requirements.cache
        return jobStore.create(command=command, predecessorNumber=predecessorNumber, **requirements)