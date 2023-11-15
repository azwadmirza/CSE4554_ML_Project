    def __init__(self, config, maxCores, maxMemory, maxDisk, masterAddress,
                 userScript=None, toilDistribution=None):
        AbstractBatchSystem.__init__(self, config, maxCores, maxMemory, maxDisk)
        # The hot-deployed resources representing the user script and the toil distribution
        # respectively. Will be passed along in every Mesos task. See
        # toil.common.HotDeployedResource for details.
        self.userScript = userScript
        self.toilDistribution = toilDistribution

        # Written to when mesos kills tasks, as directed by toil
        self.killedSet = set()

        # Dictionary of queues, which toil assigns jobs to. Each queue represents a job type,
        # defined by resource usage
        self.jobQueueList = defaultdict(list)

        # Address of Mesos master in the form host:port where host can be an IP or a hostname
        self.masterAddress = masterAddress

        # queue of jobs to kill, by jobID.
        self.killSet = set()

        # contains jobs on which killBatchJobs were called,
        #regardless of whether or not they actually were killed or
        #ended by themselves.
        self.intendedKill = set()

        # Dict of launched jobIDs to TaskData named tuple. Contains start time, executorID, and slaveID.
        self.runningJobMap = {}

        # Queue of jobs whose status has been updated, according to mesos. Req'd by toil
        self.updatedJobsQueue = Queue()

        # Whether to use implicit/explicit acknowledgments
        self.implicitAcknowledgements = self.getImplicit()

        # Reference to the Mesos driver used by this scheduler, to be instantiated in run()
        self.driver = None

        # FIXME: This comment makes no sense to me

        # Returns Mesos executor object, which is merged into Mesos tasks as they are built
        self.executor = self.buildExecutor()

        self.nextJobID = 0
        self.lastReconciliation = time.time()
        self.reconciliationPeriod = 120

        # Start the driver
        self._startDriver()