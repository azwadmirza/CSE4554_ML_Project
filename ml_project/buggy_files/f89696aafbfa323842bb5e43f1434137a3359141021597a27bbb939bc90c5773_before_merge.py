    def worker(self, inputQueue):
        while True:
            args = inputQueue.get()
            if args is None:
                log.debug('Received queue sentinel.')
                break
            jobCommand, jobID, jobCores, jobMemory, jobDisk = args
            try:
                coreFractions = int(jobCores / self.minCores)
                log.debug('Acquiring %i bytes of memory from a pool of %s.', jobMemory, self.memory)
                with self.memory.acquisitionOf(jobMemory):
                    log.debug('Acquiring %i fractional cores from a pool of %s to satisfy a '
                              'request of %f cores', coreFractions, self.coreFractions, jobCores)
                    with self.coreFractions.acquisitionOf(coreFractions):
                        log.info("Executing command: '%s'.", jobCommand)
                        with self.popenLock:
                            popen = subprocess.Popen(jobCommand, shell=True)
                        info = Info(time.time(), popen, killIntended=False)
                        self.runningJobs[jobID] = info
                        try:
                            statusCode = popen.wait()
                            if 0 != statusCode:
                                if statusCode != -9 or not info.killIntended:
                                    log.error(
                                        "Got exit code %i (indicating failure) from command '%s'.",
                                        statusCode, jobCommand)
                        finally:
                            self.runningJobs.pop(jobID)
            finally:
                log.debug('Finished job. self.coreFractions ~ %s and self.memory ~ %s',
                          self.coreFractions.value, self.memory.value)
                if not info.killIntended:
                    self.outputQueue.put((jobID, statusCode))
        log.debug('Exiting worker thread normally.')