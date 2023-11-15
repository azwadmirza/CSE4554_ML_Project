    def _createEmptyJobForJob(self, jobStore, command=None,
                                 predecessorNumber=0):
        """
        Create an empty job for the job.
        """
        memory=(self.memory if self.memory is not None
               else float(jobStore.config.defaultMemory))
        cores=(self.cores if self.cores is not None
               else float(jobStore.config.defaultCores))
        disk=(self.disk if self.disk is not None
              else float(jobStore.config.defaultDisk))
        cache=(self.cache if self.cache is not None
              else float(jobStore.config.defaultCache))
        
        if cache > disk:
            raise RuntimeError("Trying to allocate a cache (cache: %s) larger"
                               " than the disk requirement for the job! (disk: %s)" % (cache, disk))

        return jobStore.create(command=command,
                               memory=memory, cores=cores, disk=disk,
                               predecessorNumber=predecessorNumber)