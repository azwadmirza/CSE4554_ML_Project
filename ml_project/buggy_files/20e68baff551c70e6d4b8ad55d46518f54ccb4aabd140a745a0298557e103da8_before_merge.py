    def readStatsAndLogging( self, statsAndLoggingCallBackFn):
        numberOfFilesProcessed = 0
        for tempDir in self._tempDirectories():
            for tempFile in os.listdir(tempDir):
                if tempFile.startswith( 'stats' ):
                    absTempFile = os.path.join(tempDir, tempFile)
                    if not tempFile.endswith( '.new' ):
                        with open(absTempFile, 'r') as fH:
                            statsAndLoggingCallBackFn(fH)
                        numberOfFilesProcessed += 1
                        os.remove(absTempFile)
        return numberOfFilesProcessed