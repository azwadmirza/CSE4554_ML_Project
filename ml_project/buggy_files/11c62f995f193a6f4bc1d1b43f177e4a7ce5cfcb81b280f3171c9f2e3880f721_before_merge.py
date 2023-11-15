    def _startParasol(self, numCores=None, memory=None):
        if numCores is None:
            numCores = multiprocessing.cpu_count()
        if memory is None:
            memory = self._physicalMemory()
        self.numCores = numCores
        self.memory = memory
        self.leader = self.ParasolLeaderThread()
        self.leader.start()
        self.worker = self.ParasolWorkerThread()
        self.worker.start()
        while self.leader.popen is None or self.worker.popen is None:
            log.info('Waiting for leader and worker processes')
            time.sleep(.1)