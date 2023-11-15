    def issueBatchJob(self, command, memory, cores, disk):
        """
        Issues the following command returning a unique jobID. Command is the string to run, memory is an int giving
        the number of bytes the job needs to run in and cores is the number of cpus needed for the job and error-file
        is the path of the file to place any std-err/std-out in.
        """
        # puts job into job_type_queue to be run by Mesos, AND puts jobID in current_job[]
        self.checkResourceRequest(memory, cores, disk)
        jobID = self.nextJobID
        self.nextJobID += 1

        job = ToilJob(jobID=jobID,
                      resources=ResourceRequirement(memory=memory, cores=cores, disk=disk),
                      command=command,
                      userScript=self.userScript,
                      toilDistribution=self.toilDistribution,
                      environment=self.environment.copy())
        job_type = job.resources

        log.debug("Queueing the job command: %s with job id: %s ..." % (command, str(jobID)))
        self.jobQueueList[job_type].append(job)
        log.debug("... queued")

        return jobID