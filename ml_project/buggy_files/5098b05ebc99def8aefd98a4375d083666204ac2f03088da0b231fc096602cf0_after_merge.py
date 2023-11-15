    def __init__(self, config=None, executors=None, lazyErrors=True, appCache=True,
                 rundir=None, retries=0, checkpointFiles=None, checkpointMode=None,
                 data_manager=None):
        """ Initialize the DataFlowKernel.

        Please note that keyword args passed to the DFK here will always override
        options passed in via the config.

        KWargs:
            - config (dict) : A single data object encapsulating all config attributes
            - executors (list of Executor objs): Optional, kept for (somewhat) backward compatibility with 0.2.0
            - lazyErrors(bool) : Default=True, allow workflow to continue on app failures.
            - appCache (bool) :Enable caching of apps
            - rundir (str) : Path to run directory. Defaults to ./runinfo/runNNN
            - retries(int): Default=0, Set the number of retry attempts in case of failure
            - checkpointFiles (list of str): List of filepaths to checkpoint files
            - checkpointMode (None, 'dfk_exit', 'task_exit', 'periodic'): Method to use.
            - data_manager (DataManager): User created DataManager
        Returns:
            DataFlowKernel object
        """
        # Create run dirs for this run
        self.rundir = make_rundir(config=config, path=rundir)
        parsl.set_file_logger("{}/parsl.log".format(self.rundir),
                              level=logging.DEBUG)

        logger.info("Parsl version: {}".format(get_version()))
        logger.info("Libsubmit version: {}".format(libsubmit.__version__))

        # Update config with defaults
        self._config = update_config(config, self.rundir)

        # Set the data manager
        if data_manager:
            self.data_manager = data_manager
        else:
            self.data_manager = DataManager(config=self._config)

        # Start the anonymized usage tracker and send init msg
        self.usage_tracker = UsageTracker(self)
        self.usage_tracker.send_message()

        # Load Memoizer with checkpoints before we start the run.
        if checkpointFiles:
            checkpoint_src = checkpointFiles
        elif self._config and self._config["globals"]["checkpointFiles"]:
            checkpoint_src = self._config["globals"]["checkpointFiles"]
        else:
            checkpoint_src = None

        cpts = self.load_checkpoints(checkpoint_src)
        # Initialize the memoizer
        self.memoizer = Memoizer(self, memoize=appCache, checkpoint=cpts)
        self.checkpointed_tasks = 0
        self._checkpoint_timer = None

        if self._config:
            self._executors_managed = True
            # Create the executors
            epf = EPF()
            self.executors = epf.make(self.rundir, self._config)

            # set global vars from config
            self.lazy_fail = self._config["globals"].get("lazyErrors", lazyErrors)
            self.fail_retries = self._config["globals"].get("retries", retries)
            self.flowcontrol = FlowControl(self, self._config)
            self.checkpoint_mode = self._config["globals"].get("checkpointMode",
                                                               checkpointMode)
            if self.checkpoint_mode == "periodic":
                period = self._config["globals"].get("checkpointPeriod",
                                                     "00:30:00")
                try:
                    h, m, s = map(int, period.split(':'))
                    checkpoint_period = (h * 3600) + (m * 60) + s
                    self._checkpoint_timer = Timer(self.checkpoint, interval=checkpoint_period)
                except Exception as e:
                    logger.error("invalid checkpointPeriod provided:{0} expected HH:MM:SS".format(period))
                    self._checkpoint_timer = Timer(self.checkpoint, interval=(30 * 60))

        else:
            self._executors_managed = False
            self.fail_retries = retries
            self.lazy_fail = lazyErrors
            self.executors = {i: x for i, x in enumerate(executors)}
            self.flowcontrol = FlowNoControl(self, None)
            self.checkpoint_mode = checkpointMode

        self.task_count = 0
        self.fut_task_lookup = {}
        self.tasks = {}
        self.task_launch_lock = threading.Lock()

        logger.debug("Using executors: {0}".format(self.executors))
        atexit.register(self.cleanup)