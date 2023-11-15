    def issueBatchJob(self, command, memory, cores, disk):
        """
        Adds the command and resources to a queue to be run.
        """
        # Round cores to minCores and apply scale
        cores = math.ceil(cores * self.scale / self.minCores) * self.minCores
        assert cores <= self.maxCores, \
            'job is requesting {} cores, which is greater than {} available on the machine. Scale currently set ' \
            'to {} consider adjusting job or scale.'.format(cores, self.maxCores, self.scale)
        assert cores >= self.minCores
        assert memory <= self.maxMemory, 'job requests {} mem, only {} total available.'.format(
            memory, self.maxMemory)

        self.checkResourceRequest(memory, cores, disk)
        log.debug("Issuing the command: %s with memory: %i, cores: %i, disk: %i" % (
            command, memory, cores, disk))
        with self.jobIndexLock:
            jobID = self.jobIndex
            self.jobIndex += 1
        self.jobs[jobID] = command
        self.inputQueue.put((command, jobID, cores, memory, disk))
        return jobID