    def readStatsAndLogging(self, statsAndLoggingCallBackFn):
        """
        Reads stats/logging strings accumulated by "writeStatsAndLogging" function. 
        For each stats/logging file calls the statsAndLoggingCallBackFn with 
        an open, readable file-handle that can be used to parse the stats.
        Returns the number of stat/logging strings processed. 
        Stats/logging files are only read once and are removed from the 
        file store after being written to the given file handle.
        """
        raise NotImplementedError()