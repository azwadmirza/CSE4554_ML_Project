    def readStatsAndLogging(self, callback, readAll=False):
        numberOfFilesProcessed = 0
        for tempDir in self._tempDirectories():
            for tempFile in os.listdir(tempDir):
                if tempFile.startswith('stats'):
                    absTempFile = os.path.join(tempDir, tempFile)
                    if readAll or not tempFile.endswith('.new'):
                        with open(absTempFile, 'r') as fH:
                            callback(fH)
                        numberOfFilesProcessed += 1
                        newName = tempFile.rsplit('.', 1)[0] + '.new'
                        newAbsTempFile = os.path.join(tempDir, newName)
                        # Mark this item as read
                        os.rename(absTempFile, newAbsTempFile)
        return numberOfFilesProcessed