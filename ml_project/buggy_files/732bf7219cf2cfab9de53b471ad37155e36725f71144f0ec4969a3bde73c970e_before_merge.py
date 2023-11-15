    def setOptions(self, options):
        """
        Creates a config object from the options object.
        """
        from bd2k.util.humanize import human2bytes #This import is used to convert
        #from human readable quantites to integers
        def setOption(varName, parsingFn=None, checkFn=None):
            #If options object has the option "varName" specified
            #then set the "varName" attrib to this value in the config object
            x = getattr(options, varName, None)
            if x != None:
                if parsingFn != None:
                    x = parsingFn(x)
                if checkFn != None:
                    try:
                        checkFn(x)
                    except AssertionError:
                        raise RuntimeError("The %s option has an invalid value: %s"
                                           % (varName, x))
                setattr(self, varName, x)

        # Function to parse integer from string expressed in different formats
        h2b = lambda x : human2bytes(str(x))

        def iC(minValue, maxValue=sys.maxint):
            # Returns function that checks if a given int is in the given half-open interval
            assert isinstance(minValue, int) and isinstance(maxValue, int)
            return lambda x: minValue <= x < maxValue

        def fC(minValue, maxValue=None):
            # Returns function that checks if a given float is in the given half-open interval
            assert isinstance(minValue, float)
            if maxValue is None:
                return lambda x: minValue <= x
            else:
                assert isinstance(maxValue, float)
                return lambda x: minValue <= x < maxValue

        #Core options
        setOption("jobStore",
                  parsingFn=lambda x: os.path.abspath(x) if options.jobStore.startswith('.') else x)
        #TODO: LOG LEVEL STRING
        setOption("workDir")
        setOption("stats")
        setOption("clean")
        if self.stats:
            if self.clean != "never" and self.clean is not None:
                raise RuntimeError("Contradicting options passed: Clean flag is set to %s "
                                   "despite the stats flag requiring "
                                   "the jobStore to be intact at the end of the run. "
                                   "Set clean to \'never\'" % self.clean)
            self.clean = "never"
        elif self.clean is None:
            self.clean = "onSuccess"

        #Restarting the workflow options
        setOption("restart")

        #Batch system options
        setOption("batchSystem")
        setOption("scale", float, fC(0.0))
        setOption("mesosMasterAddress")
        setOption("parasolCommand")
        setOption("parasolMaxBatches", int, iC(1))

        setOption("environment", parseSetEnv)

        #Resource requirements
        setOption("defaultMemory", h2b, iC(1))
        setOption("defaultCores", float, fC(1.0))
        setOption("defaultDisk", h2b, iC(1))
        setOption("defaultCache", h2b, iC(0))
        setOption("maxCores", int, iC(1))
        setOption("maxMemory", h2b, iC(1))
        setOption("maxDisk", h2b, iC(1))

        #Retrying/rescuing jobs
        setOption("retryCount", int, iC(0))
        setOption("maxJobDuration", int, iC(1))
        setOption("rescueJobsFrequency", int, iC(1))

        #Misc
        setOption("maxLogFileSize", h2b, iC(1))
        def checkSse(sseKey):
            with open(sseKey) as f:
                assert(len(f.readline().rstrip()) == 32)
        setOption("sseKey", checkFn=checkSse)
        setOption("cseKey", checkFn=checkSse)

        #Debug options
        setOption("badWorker", float, fC(0.0, 1.0))
        setOption("badWorkerFailInterval", float, fC(0.0))