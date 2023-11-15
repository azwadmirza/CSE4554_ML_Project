    def __init__(self):
        # Core options
        self.workflowID = None
        """This attribute uniquely identifies the job store and therefore the workflow. It is
        necessary in order to distinguish between two consequitive workflows for which
        self.jobStore is the same, e.g. when a job store name is reused after a previous run has
        finished sucessfully and its job store has been clean up."""
        self.workflowAttemptNumber = None
        self.jobStore = os.path.abspath("./toil")
        self.logLevel = getLogLevelString()
        self.workDir = None
        self.stats = False

        # Because the stats option needs the jobStore to persist past the end of the run,
        # the clean default value depends the specified stats option and is determined in setOptions
        self.clean = None
        self.cleanWorkDir = None

        #Restarting the workflow options
        self.restart = False

        #Batch system options
        self.batchSystem = "singleMachine"
        self.scale = 1
        self.mesosMasterAddress = 'localhost:5050'
        self.parasolCommand = "parasol"
        self.parasolMaxBatches = 10000
        self.environment = {}

        #Autoscaling options
        self.provisioner = None
        self.preemptableNodeType = None
        self.preemptableNodeOptions = None
        self.preemptableBidPrice = None
        self.minPreemptableNodes = 0
        self.maxPreemptableNodes = 10
        self.nodeType = None
        self.nodeOptions = None
        self.minNodes = 0
        self.maxNodes = 10
        self.alphaPacking = 0.8
        self.betaInertia = 1.2
        self.scaleInterval = 360

        #Resource requirements
        self.defaultMemory = 2147483648
        self.defaultCores = 1
        self.defaultDisk = 2147483648
        self.readGlobalFileMutableByDefault = False
        self.defaultPreemptable = False
        self.maxCores = sys.maxint
        self.maxMemory = sys.maxint
        self.maxDisk = sys.maxint

        #Retrying/rescuing jobs
        self.retryCount = 0
        self.maxJobDuration = sys.maxint
        self.rescueJobsFrequency = 3600

        #Misc
        self.maxLogFileSize=50120
        self.sseKey = None
        self.cseKey = None
        self.servicePollingInterval = 60
        self.useAsync = True


        #Debug options
        self.badWorker = 0.0
        self.badWorkerFailInterval = 0.01