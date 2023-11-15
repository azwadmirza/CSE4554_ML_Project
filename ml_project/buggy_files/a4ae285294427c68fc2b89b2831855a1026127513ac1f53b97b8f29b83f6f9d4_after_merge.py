    def issueBatchJob(self, command, memory, cores, disk, preemptable):
        """
        Issues the following command returning a unique jobID. Command is the string to run, memory
        is an int giving the number of bytes the job needs to run in and cores is the number of cpus
        needed for the job and error-file is the path of the file to place any std-err/std-out in.
        """
        self.checkResourceRequest(memory, cores, disk)
        jobID = next(self.unusedJobID)
        job = ToilJob(jobID=jobID,
                      resources=ResourceRequirement(memory=memory,
                                                    cores=cores,
                                                    disk=disk,
                                                    preemptable=preemptable),
                      command=command,
                      userScript=self.userScript,
                      environment=self.environment.copy(),
                      workerCleanupInfo=self.workerCleanupInfo)
        jobType = job.resources
        log.debug("Queueing the job command: %s with job id: %s ...", command, str(jobID))
        self.jobQueues[jobType].append(job)
        log.debug("... queued")
        return jobID