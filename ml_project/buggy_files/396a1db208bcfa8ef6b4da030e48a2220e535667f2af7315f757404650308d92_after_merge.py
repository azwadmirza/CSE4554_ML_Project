    def __init__(
        self,
        logger: Union[LightningLoggerBase, Iterable[LightningLoggerBase], bool] = True,
        checkpoint_callback: Union[ModelCheckpoint, bool] = True,
        early_stop_callback: Optional[Union[EarlyStopping, bool]] = False,
        callbacks: Optional[List[Callback]] = None,
        default_root_dir: Optional[str] = None,
        gradient_clip_val: float = 0,
        process_position: int = 0,
        num_nodes: int = 1,
        num_processes: int = 1,
        gpus: Optional[Union[List[int], str, int]] = None,
        auto_select_gpus: bool = False,
        tpu_cores: Optional[Union[List[int], str, int]] = None,
        log_gpu_memory: Optional[str] = None,
        progress_bar_refresh_rate: int = 1,
        overfit_batches: Union[int, float] = 0.0,
        track_grad_norm: Union[int, float, str] = -1,
        check_val_every_n_epoch: int = 1,
        fast_dev_run: bool = False,
        accumulate_grad_batches: Union[int, Dict[int, int], List[list]] = 1,
        max_epochs: int = 1000,
        min_epochs: int = 1,
        max_steps: Optional[int] = None,
        min_steps: Optional[int] = None,
        limit_train_batches: Union[int, float] = 1.0,
        limit_val_batches: Union[int, float] = 1.0,
        limit_test_batches: Union[int, float] = 1.0,
        val_check_interval: Union[int, float] = 1.0,
        log_save_interval: int = 100,
        row_log_interval: int = 50,
        distributed_backend: Optional[str] = None,
        precision: int = 32,
        print_nan_grads: bool = False,  # backward compatible, todo: remove in v0.9.0
        weights_summary: Optional[str] = ModelSummary.MODE_DEFAULT,
        weights_save_path: Optional[str] = None,
        num_sanity_val_steps: int = 2,
        truncated_bptt_steps: Optional[int] = None,
        resume_from_checkpoint: Optional[str] = None,
        profiler: Optional[Union[BaseProfiler, bool]] = None,
        benchmark: bool = False,
        deterministic: bool = False,
        reload_dataloaders_every_epoch: bool = False,
        auto_lr_find: Union[bool, str] = False,
        replace_sampler_ddp: bool = True,
        terminate_on_nan: bool = False,
        auto_scale_batch_size: Union[str, bool] = False,
        prepare_data_per_node: bool = True,
        amp_level: str = 'O2',  # backward compatible, todo: remove in v1.0.0
        num_tpu_cores: Optional[int] = None,  # backward compatible, todo: remove in v0.9.0
        use_amp=None,  # backward compatible, todo: remove in v0.9.0
        show_progress_bar=None,  # backward compatible, todo: remove in v0.9.0
        val_percent_check: float = None,  # backward compatible, todo: remove in v0.10.0
        test_percent_check: float = None,  # backward compatible, todo: remove in v0.10.0
        train_percent_check: float = None,  # backward compatible, todo: remove in v0.10.0
        overfit_pct: float = None,  # backward compatible, todo: remove in v1.0.0
    ):
        r"""

        Customize every aspect of training via flags

        Args:
            logger: Logger (or iterable collection of loggers) for experiment tracking.

            checkpoint_callback: Callback for checkpointing.

            early_stop_callback (:class:`pytorch_lightning.callbacks.EarlyStopping`):

            callbacks: Add a list of callbacks.

            default_root_dir: Default path for logs and weights when no logger/ckpt_callback passed.
                Default: ``os.getcwd()``.

            gradient_clip_val: 0 means don't clip.

            gradient_clip:
                .. warning:: .. deprecated:: 0.7.0

                    Use `gradient_clip_val` instead. Will remove 0.9.0.

            process_position: orders the progress bar when running multiple models on same machine.

            num_nodes: number of GPU nodes for distributed training.

            nb_gpu_nodes:
                .. warning:: .. deprecated:: 0.7.0

                    Use `num_nodes` instead. Will remove 0.9.0.

            gpus: Which GPUs to train on.

            auto_select_gpus:

                If enabled and `gpus` is an integer, pick available
                gpus automatically. This is especially useful when
                GPUs are configured to be in "exclusive mode", such
                that only one process at a time can access them.

            tpu_cores: How many TPU cores to train on (1 or 8) / Single TPU to train on [1]

            num_tpu_cores: How many TPU cores to train on (1 or 8)
                .. warning:: .. deprecated:: 0.7.6. Will remove 0.9.0.

            log_gpu_memory: None, 'min_max', 'all'. Might slow performance

            show_progress_bar:
                .. warning:: .. deprecated:: 0.7.2

                        Set `progress_bar_refresh_rate` to positive integer to enable. Will remove 0.9.0.

            progress_bar_refresh_rate: How often to refresh progress bar (in steps). Value ``0`` disables progress bar.
                Ignored when a custom callback is passed to :paramref:`~Trainer.callbacks`.

            overfit_batches: Overfit a percent of training data (float) or a set number of batches (int). Default: 0.0

            overfit_pct:
                .. warning:: .. deprecated:: 0.8.0

                    Use `overfit_batches` instead. Will be removed in 0.10.0.

            track_grad_norm: -1 no tracking. Otherwise tracks that p-norm. May be set to 'inf' infinity-norm.

            check_val_every_n_epoch: Check val every n train epochs.

            fast_dev_run: runs 1 batch of train, test and val to find any bugs (ie: a sort of unit test).

            accumulate_grad_batches: Accumulates grads every k batches or as set up in the dict.

            max_epochs: Stop training once this number of epochs is reached.

            max_nb_epochs:
                .. warning:: .. deprecated:: 0.7.0

                    Use `max_epochs` instead. Will remove 0.9.0.

            min_epochs: Force training for at least these many epochs

            min_nb_epochs:
                .. warning:: .. deprecated:: 0.7.0

                    Use `min_epochs` instead. Will remove 0.9.0.

            max_steps: Stop training after this number of steps. Disabled by default (None).

            min_steps: Force training for at least these number of steps. Disabled by default (None).

            limit_train_batches: How much of training dataset to check (floats = percent, int = num_batches)

            limit_val_batches: How much of validation dataset to check (floats = percent, int = num_batches)

            limit_test_batches: How much of test dataset to check (floats = percent, int = num_batches)

            train_percent_check:
                .. warning:: .. deprecated:: 0.8.0

                    Use `limit_train_batches` instead. Will remove v0.10.0.

            val_percent_check:
                .. warning:: .. deprecated:: 0.8.0

                    Use `limit_val_batches` instead. Will remove v0.10.0.

            test_percent_check:
                .. warning:: .. deprecated:: 0.8.0

                    Use `limit_test_batches` instead. Will remove v0.10.0.

            val_check_interval: How often within one training epoch to check the validation set

            log_save_interval: Writes logs to disk this often

            row_log_interval: How often to add logging rows (does not write to disk)

            add_row_log_interval:
                .. warning:: .. deprecated:: 0.7.0

                    Use `row_log_interval` instead. Will remove 0.9.0.

            distributed_backend: The distributed backend to use (dp, ddp, ddp2, ddp_spawn, ddp_cpu)

            use_amp:
                .. warning:: .. deprecated:: 0.7.0

                    Use `precision` instead. Will remove 0.9.0.

            precision: Full precision (32), half precision (16).

            print_nan_grads:
                .. warning:: .. deprecated:: 0.7.2

                    Has no effect. When detected, NaN grads will be printed automatically.
                    Will remove 0.9.0.

            weights_summary: Prints a summary of the weights when training begins.

            weights_save_path: Where to save weights if specified. Will override default_root_dir
                    for checkpoints only. Use this if for whatever reason you need the checkpoints
                    stored in a different place than the logs written in `default_root_dir`.
                    Defaults to `default_root_dir`.

            amp_level: The optimization level to use (O1, O2, etc...).

            num_sanity_val_steps: Sanity check runs n validation batches before starting the training routine.
                Set it to `-1` to run all batches in all validation dataloaders. Default: 2

            truncated_bptt_steps: Truncated back prop breaks performs backprop every k steps of

            resume_from_checkpoint: To resume training from a specific checkpoint pass in the path here.
                This can be a URL.

            profiler:  To profile individual steps during training and assist in

            reload_dataloaders_every_epoch: Set to True to reload dataloaders every epoch

            auto_lr_find: If set to True, will `initially` run a learning rate finder,
                trying to optimize initial learning for faster convergence. Sets learning
                rate in self.lr or self.learning_rate in the LightningModule.
                To use a different key, set a string instead of True with the key name.

            replace_sampler_ddp: Explicitly enables or disables sampler replacement.
                If not specified this will toggled automatically ddp is used

            benchmark: If true enables cudnn.benchmark.

            deterministic: If true enables cudnn.deterministic

            terminate_on_nan: If set to True, will terminate training (by raising a `ValueError`) at the
                end of each training batch, if any of the parameters or the loss are NaN or +/-inf.

            auto_scale_batch_size: If set to True, will `initially` run a batch size
                finder trying to find the largest batch size that fits into memory.
                The result will be stored in self.batch_size in the LightningModule.
                Additionally, can be set to either `power` that estimates the batch size through
                a power search or `binsearch` that estimates the batch size through a binary search.

            prepare_data_per_node: If True, each LOCAL_RANK=0 will call prepare data.
                Otherwise only NODE_RANK=0, LOCAL_RANK=0 will prepare data
        """
        super().__init__()

        self.deterministic = deterministic
        torch.backends.cudnn.deterministic = self.deterministic
        if self.deterministic:
            # fixing non-deterministic part of horovod
            # https://github.com/PyTorchLightning/pytorch-lightning/pull/1572/files#r420279383
            os.environ["HOROVOD_FUSION_THRESHOLD"] = str(0)

        # init the default rank if exists
        # we need to call this here or NVIDIA flags and other messaging in init will show on all ranks
        # this way we only show it on rank 0
        if 'LOCAL_RANK' in os.environ:
            rank_zero_only.rank = int(os.environ['LOCAL_RANK'])

        # training bookeeping
        self.total_batch_idx = 0
        self.running_loss = TensorRunningAccum(window_length=20)
        self.batch_idx = 0
        self.progress_bar_metrics = {}
        self.callback_metrics = {}
        self.num_training_batches = 0
        self.num_val_batches = []
        self.num_test_batches = []
        self.train_dataloader = None
        self.test_dataloaders = None
        self.val_dataloaders = None

        # when true, prints test results
        self.verbose_test = True

        # when .test() is called, it sets this
        self.tested_ckpt_path = None

        # training state
        self.model = None
        self.testing = False
        self.prepare_data_per_node = prepare_data_per_node
        self.lr_schedulers = []
        self.optimizers = None
        self.optimizer_frequencies = []
        self.global_step = 0
        self.current_epoch = 0
        self.interrupted = False
        self.should_stop = False
        self.running_sanity_check = False

        self._default_root_dir = default_root_dir or os.getcwd()
        self._weights_save_path = weights_save_path or self._default_root_dir

        # init callbacks
        self.callbacks = callbacks or []

        # configure early stop callback
        # creates a default one if none passed in
        early_stop_callback = self.configure_early_stopping(early_stop_callback)
        if early_stop_callback:
            self.callbacks.append(early_stop_callback)

        # configure checkpoint callback
        # it is important that this is the last callback to run
        # pass through the required args to figure out defaults
        checkpoint_callback = self.configure_checkpoint_callback(checkpoint_callback)
        if checkpoint_callback:
            self.callbacks.append(checkpoint_callback)

        # TODO refactor codebase (tests) to not directly reach into these callbacks
        self.checkpoint_callback = checkpoint_callback
        self.early_stop_callback = early_stop_callback

        self.on_init_start()

        # benchmarking
        self.benchmark = benchmark
        torch.backends.cudnn.benchmark = self.benchmark

        # Transfer params
        self.num_nodes = num_nodes
        self.log_gpu_memory = log_gpu_memory

        self.gradient_clip_val = gradient_clip_val
        self.check_val_every_n_epoch = check_val_every_n_epoch

        if not isinstance(track_grad_norm, (int, float)) and track_grad_norm != 'inf':
            raise MisconfigurationException("track_grad_norm can be an int, a float or 'inf' (infinity norm).")
        self.track_grad_norm = float(track_grad_norm)

        # tpu config
        if num_tpu_cores is not None:
            rank_zero_warn(
                "Argument `num_tpu_cores` is now set by `tpu_cores` since v0.7.6"
                " and this argument will be removed in v0.9.0",
                DeprecationWarning,
            )

        if tpu_cores is None:
            tpu_cores = num_tpu_cores
        self.tpu_cores = _parse_tpu_cores(tpu_cores)
        self.on_tpu = self.tpu_cores is not None

        self.tpu_id = self.tpu_cores[0] if isinstance(self.tpu_cores, list) else None

        if num_processes != 1 and distributed_backend != "ddp_cpu":
            rank_zero_warn("num_processes is only used for distributed_backend=\"ddp_cpu\". Ignoring it.")
        self.num_processes = num_processes

        self.weights_summary = weights_summary

        self.max_epochs = max_epochs
        self.min_epochs = min_epochs
        self.max_steps = max_steps
        self.min_steps = min_steps

        if num_sanity_val_steps == -1:
            self.num_sanity_val_steps = float("inf")
        else:
            self.num_sanity_val_steps = min(num_sanity_val_steps, limit_val_batches)

        # Backward compatibility, TODO: remove in v0.9.0
        if print_nan_grads:
            rank_zero_warn(
                "Argument `print_nan_grads` has no effect and will be removed in v0.9.0."
                " NaN grads will be printed automatically when detected.",
                DeprecationWarning,
            )

        self.reload_dataloaders_every_epoch = reload_dataloaders_every_epoch

        self.auto_lr_find = auto_lr_find
        self.auto_scale_batch_size = auto_scale_batch_size
        self._is_data_prepared = False
        self.replace_sampler_ddp = replace_sampler_ddp

        self.truncated_bptt_steps = truncated_bptt_steps
        self.resume_from_checkpoint = resume_from_checkpoint
        self.terminate_on_nan = terminate_on_nan
        self.shown_warnings = set()

        self.fast_dev_run = fast_dev_run
        if self.fast_dev_run:
            limit_train_batches = 1
            limit_val_batches = 1
            limit_test_batches = 1
            self.num_sanity_val_steps = 0
            self.max_epochs = 1
            rank_zero_info(
                'Running in fast_dev_run mode: will run a full train,' ' val and test loop using a single batch'
            )

        # configure profiler
        if profiler is True:
            profiler = SimpleProfiler()
        self.profiler = profiler or PassThroughProfiler()

        # accumulated grads
        self.accumulate_grad_batches = accumulate_grad_batches
        self.configure_accumulated_gradients(accumulate_grad_batches)

        # for gpus allow int, string and gpu list
        if auto_select_gpus and isinstance(gpus, int):
            self.gpus = pick_multiple_gpus(gpus)
        else:
            self.gpus = gpus

        self.data_parallel_device_ids = _parse_gpu_ids(self.gpus)
        self.root_gpu = determine_root_gpu_device(self.data_parallel_device_ids)
        self.root_device = torch.device("cpu")

        self.on_gpu = True if (self.data_parallel_device_ids and torch.cuda.is_available()) else False

        # tpu state flags
        self.use_tpu = False
        self.tpu_local_core_rank = None
        self.tpu_global_core_rank = None

        # distributed backend choice
        self.distributed_backend = distributed_backend
        self.set_distributed_mode(distributed_backend)

        # override dist backend when using tpus
        if self.on_tpu:
            self.init_tpu()

        # init flags for SLURM+DDP to work
        self.world_size = 1
        self.interactive_ddp_procs = []
        self.configure_slurm_ddp(self.num_nodes)
        self.node_rank = self.determine_ddp_node_rank()
        self.local_rank = self.determine_local_rank()
        self.global_rank = 0

        # NVIDIA setup
        self.set_nvidia_flags(self.is_slurm_managing_tasks, self.data_parallel_device_ids)

        # backward compatibility
        if show_progress_bar is not None:
            self.show_progress_bar = show_progress_bar

        self._progress_bar_callback = self.configure_progress_bar(progress_bar_refresh_rate, process_position)

        # logging
        self.configure_logger(logger)
        self.log_save_interval = log_save_interval
        self.val_check_interval = val_check_interval
        self.row_log_interval = row_log_interval

        # how much of the data to use
        # TODO: remove in 0.10.0
        if overfit_pct is not None:
            rank_zero_warn(
                "Argument `overfit_pct` is now set by `overfit_batches` since v0.8.0"
                " and this argument will be removed in v0.10.0",
                DeprecationWarning,
            )
            overfit_batches = overfit_pct

        # convert floats to ints
        self.overfit_batches = _determine_limit_batches(overfit_batches)

        # TODO: remove in 0.10.0
        if val_percent_check is not None:
            rank_zero_warn(
                "Argument `val_percent_check` is now set by `limit_val_batches` since v0.8.0"
                " and this argument will be removed in v0.10.0",
                DeprecationWarning,
            )
            limit_val_batches = val_percent_check

        # TODO: remove in 0.10.0
        if test_percent_check is not None:
            rank_zero_warn(
                "Argument `test_percent_check` is now set by `limit_test_batches` since v0.8.0"
                " and this argument will be removed in v0.10.0",
                DeprecationWarning,
            )
            limit_test_batches = test_percent_check

        # TODO: remove in 0.10.0
        if train_percent_check is not None:
            rank_zero_warn(
                "Argument `train_percent_check` is now set by `limit_train_batches` since v0.8.0"
                " and this argument will be removed in v0.10.0",
                DeprecationWarning,
            )
            limit_train_batches = train_percent_check

        self.limit_test_batches = _determine_limit_batches(limit_test_batches)
        self.limit_val_batches = _determine_limit_batches(limit_val_batches)
        self.limit_train_batches = _determine_limit_batches(limit_train_batches)
        self.determine_data_use_amount(self.overfit_batches)

        # AMP init
        # These are the only lines needed after v0.8.0
        # we wrap the user's forward with autocast and give it back at the end of fit
        self.autocast_original_forward = None
        self.precision = precision
        self.scaler = None

        # Backward compatibility, TODO: remove in v0.9.0
        if use_amp is not None:
            rank_zero_warn(
                "Argument `use_amp` is now set by `precision` since v0.7.0"
                " and this method will be removed in v0.9.0",
                DeprecationWarning,
            )
            self.precision = 16 if use_amp else 32

        self.amp_level = amp_level
        self.init_amp()

        self.on_colab_kaggle = os.getenv('COLAB_GPU') or os.getenv('KAGGLE_URL_BASE')

        # tracks internal state for debugging
        self.dev_debugger = InternalDebugger(self)
        self.config_validator = ConfigValidator(self)
        self.accelerator_backend = None

        # Callback system
        self.on_init_end()