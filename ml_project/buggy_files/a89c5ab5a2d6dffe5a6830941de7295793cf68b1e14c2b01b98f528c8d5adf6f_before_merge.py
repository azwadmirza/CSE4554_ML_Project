    def __init__(
            self, trainable_name, config=None, local_dir=DEFAULT_RESULTS_DIR,
            experiment_tag=None, resources=Resources(cpu=1, gpu=0),
            stopping_criterion=None, checkpoint_freq=0,
            restore_path=None, upload_dir=None, max_failures=0):
        """Initialize a new trial.

        The args here take the same meaning as the command line flags defined
        in ray.tune.config_parser.
        """

        if not _default_registry.contains(
                TRAINABLE_CLASS, trainable_name):
            raise TuneError("Unknown trainable: " + trainable_name)

        if stopping_criterion:
            for k in stopping_criterion:
                if k not in TrainingResult._fields:
                    raise TuneError(
                        "Stopping condition key `{}` must be one of {}".format(
                            k, TrainingResult._fields))

        # Trial config
        self.trainable_name = trainable_name
        self.config = config or {}
        self.local_dir = local_dir
        self.experiment_tag = experiment_tag
        self.resources = resources
        self.stopping_criterion = stopping_criterion or {}
        self.checkpoint_freq = checkpoint_freq
        self.upload_dir = upload_dir
        self.verbose = True
        self.max_failures = max_failures

        # Local trial state that is updated during the run
        self.last_result = None
        self._checkpoint_path = restore_path
        self._checkpoint_obj = None
        self.runner = None
        self.status = Trial.PENDING
        self.location = None
        self.logdir = None
        self.result_logger = None
        self.last_debug = 0
        self.trial_id = binary_to_hex(random_string())[:8]
        self.error_file = None
        self.num_failures = 0