    def __updateState(self, intID, exitStatus):
        self.updatedJobsQueue.put((intID, exitStatus))
        try:
            del self.runningJobMap[intID]
        except KeyError:
            log.warning('Cannot find %i among running jobs. '
                        'Sent update about its exit code of %i anyways.', intID, exitStatus)