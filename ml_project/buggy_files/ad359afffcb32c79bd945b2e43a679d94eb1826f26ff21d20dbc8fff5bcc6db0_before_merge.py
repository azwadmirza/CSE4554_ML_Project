    def __init__(
            self,
            logger: Union[LightningLoggerBase, Iterable[LightningLoggerBase], bool] = True,
            checkpoint_callback: Union[ModelCheckpoint, bool] = True,
            early_stop_callback: Optional[Union[EarlyStopping, bool]] = False,
            callbacks: List[Callback] = [],
            default_root_dir: Optional[str] = None,
            gradient_clip_val: float = 0,
            process_position: int = 0,
            num_nodes: int = 1,
            num_processes: int = 1,
            gpus: Optional[Union[List[int], str, int]] = None,
            auto_select_gpus: bool = False,
            num_tpu_cores: Optional[int] = None,
            log_gpu_memory: Optional[str] = None,
            progress_bar_refresh_rate: int = 1,
            overfit_pct: float = 0.0,
            track_grad_norm: int = -1,
            check_val_every_n_epoch: int = 1,
            fast_dev_run: bool = False,
            accumulate_grad_batches: Union[int, Dict[int, int], List[list]] = 1,
            max_epochs: int = 1000,
            min_epochs: int = 1,
            max_steps: Optional[int] = None,
            min_steps: Optional[int] = None,
            train_percent_check: float = 1.0,
            val_percent_check: float = 1.0,
            test_percent_check: float = 1.0,
            val_check_interval: float = 1.0,
            log_save_interval: int = 100,
            row_log_interval: int = 10,
            add_row_log_interval=None,  # backward compatible, todo: remove in v0.8.0
            distributed_backend: Optional[str] = None,
            precision: int = 32,
            print_nan_grads: bool = False,  # backward compatible, todo: remove in v0.9.0
            weights_summary: Optional[str] = 'full',
            weights_save_path: Optional[str] = None,
            amp_level: str = 'O1',
            num_sanity_val_steps: int = 5,
            truncated_bptt_steps: Optional[int] = None,
            resume_from_checkpoint: Optional[str] = None,
            profiler: Optional[BaseProfiler] = None,
            benchmark: bool = False,
            reload_dataloaders_every_epoch: bool = False,
            auto_lr_find: Union[bool, str] = False,
            default_save_path=None,  # backward compatible, todo: remove in v0.8.0
            gradient_clip=None,  # backward compatible, todo: remove in v0.8.0
            nb_gpu_nodes=None,  # backward compatible, todo: remove in v0.8.0
            max_nb_epochs=None,  # backward compatible, todo: remove in v0.8.0
            min_nb_epochs=None,  # backward compatible, todo: remove in v0.8.0
            use_amp=None,  # backward compatible, todo: remove in v0.9.0
            show_progress_bar=None,  # backward compatible, todo: remove in v0.9.0
            nb_sanity_val_steps=None,  # backward compatible, todo: remove in v0.8.0
            terminate_on_nan: bool = False,
            **kwargs
    ):
        r"""

        Customize every aspect of training via flags

        Args:
            logger: Logger (or iterable collection of loggers) for experiment tracking.

            checkpoint_callback: Callback for checkpointing.

            early_stop_callback (:class:`pytorch_lightning.callbacks.EarlyStopping`):

            callbacks: Add a list of callbacks.

            default_root_dir: Default path for logs and weights when no logger/ckpt_callback passed

            default_save_path:
                .. warning:: .. deprecated:: 0.7.3

                    Use `default_root_dir` instead. Will remove 0.9.0.

            gradient_clip_val: 0 means don't clip.

            gradient_clip:
                .. warning:: .. deprecated:: 0.7.0

                    Use `gradient_clip_val` instead. Will remove 0.9.0.

            process_position: orders the tqdm bar when running multiple models on same machine.

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

            num_tpu_cores: How many TPU cores to train on (1 or 8).

            log_gpu_memory: None, 'min_max', 'all'. Might slow performance

            show_progress_bar:
                .. warning:: .. deprecated:: 0.7.2

                        Set `progress_bar_refresh_rate` to postive integer to enable. Will remove 0.9.0.

            progress_bar_refresh_rate: How often to refresh progress bar (in steps). Value ``0`` disables progress bar.

            overfit_pct: How much of training-, validation-, and test dataset to check.

            track_grad_norm: -1 no tracking. Otherwise tracks that norm

            check_val_every_n_epoch: Check val every n train epochs.

            fast_dev_run: runs 1 batch of train, test  and val to find any bugs (ie: a sort of unit test).

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

            train_percent_check: How much of training dataset to check.

            val_percent_check: How much of validation dataset to check.

            test_percent_check: How much of test dataset to check.

            val_check_interval: How often within one training epoch to check the validation set

            log_save_interval: Writes logs to disk this often

            row_log_interval: How often to add logging rows (does not write to disk)

            add_row_log_interval:
                .. warning:: .. deprecated:: 0.7.0

                    Use `row_log_interval` instead. Will remove 0.9.0.

            distributed_backend: The distributed backend to use.

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

            amp_level: The optimization level to use (O1, O2, etc...).

            num_sanity_val_steps: Sanity check runs n batches of val before starting the training routine.

            nb_sanity_val_steps:
                .. warning:: .. deprecated:: 0.7.0

                    Use `num_sanity_val_steps` instead. Will remove 0.8.0.

            truncated_bptt_steps: Truncated back prop breaks performs backprop every k steps of

            resume_from_checkpoint: To resume training from a specific checkpoint pass in the path here.

            profiler:  To profile individual steps during training and assist in

            reload_dataloaders_every_epoch: Set to True to reload dataloaders every epoch

            auto_lr_find: If set to True, will `initially` run a learning rate finder,
                trying to optimize initial learning for faster convergence. Sets learning
                rate in self.hparams.lr | self.hparams.learning_rate in the lightning module.
                To use a different key, set a string instead of True with the key name.

            benchmark: If true enables cudnn.benchmark.

            terminate_on_nan: If set to True, will terminate training (by raising a `ValueError`) at the
                end of each training batch, if any of the parameters or the loss are NaN or +/-inf.
        """

        # Init callbacks
        self.callbacks = callbacks
        self.on_init_start()

        # benchmarking
        self.benchmark = benchmark
        torch.backends.cudnn.benchmark = self.benchmark

        # Transfer params
        self.num_nodes = num_nodes
        # Backward compatibility, TODO: remove in v0.8.0
        if nb_gpu_nodes is not None:
            rank_zero_warn("Argument `nb_gpu_nodes` has renamed to `num_nodes` since v0.5.0"
                           " and this method will be removed in v0.8.0", DeprecationWarning)
            self.num_gpu_nodes = nb_gpu_nodes
        self.log_gpu_memory = log_gpu_memory

        self.gradient_clip_val = gradient_clip_val
        # Backward compatibility, TODO: remove in v0.8.0
        if gradient_clip is not None:
            rank_zero_warn("Argument `gradient_clip` has renamed to `gradient_clip_val` since v0.5.0"
                           " and this method will be removed in v0.8.0", DeprecationWarning)
            self.gradient_clip = gradient_clip

        self.progress_bar_refresh_rate = progress_bar_refresh_rate
        self.check_val_every_n_epoch = check_val_every_n_epoch
        self.track_grad_norm = track_grad_norm
        self.on_gpu = True if (gpus and torch.cuda.is_available()) else False

        # tpu config
        self.on_tpu = num_tpu_cores is not None
        self.num_tpu_cores = num_tpu_cores
        assert num_tpu_cores in [1, 8, None], 'num_tpu_cores can only be 1 or 8'

        if num_processes != 1 and distributed_backend != "ddp_cpu":
            rank_zero_warn("num_processes is only used for distributed_backend=\"ddp_cpu\". Ignoring it.")
        self.num_processes = num_processes

        self.process_position = process_position
        self.weights_summary = weights_summary

        self.max_epochs = max_epochs
        # Backward compatibility, TODO: remove in v0.8.0
        if max_nb_epochs is not None:
            rank_zero_warn("Argument `max_nb_epochs` has renamed to `max_epochs` since v0.5.0"
                           " and this method will be removed in v0.8.0", DeprecationWarning)
            self.max_nb_epochs = max_nb_epochs

        self.min_epochs = min_epochs
        # Backward compatibility, TODO: remove in v0.8.0
        if min_nb_epochs is not None:
            rank_zero_warn("Argument `min_nb_epochs` has renamed to `min_epochs` since v0.5.0"
                           " and this method will be removed in v0.8.0", DeprecationWarning)
            self.min_nb_epochs = min_nb_epochs

        self.max_steps = max_steps
        self.min_steps = min_steps

        self.num_sanity_val_steps = num_sanity_val_steps
        # Backward compatibility, TODO: remove in v0.8.0
        if nb_sanity_val_steps is not None:
            rank_zero_warn("Argument `nb_sanity_val_steps` has renamed to "
                           "`num_sanity_val_steps` since v0.5.0"
                           " and this method will be removed in v0.8.0", DeprecationWarning)
            self.nb_sanity_val_steps = nb_sanity_val_steps

        # Backward compatibility, TODO: remove in v0.9.0
        if print_nan_grads:
            rank_zero_warn("Argument `print_nan_grads` has no effect and will be removed in v0.9.0."
                           " NaN grads will be printed automatically when detected.", DeprecationWarning)

        self.reload_dataloaders_every_epoch = reload_dataloaders_every_epoch

        self.auto_lr_find = auto_lr_find

        self.truncated_bptt_steps = truncated_bptt_steps
        self.resume_from_checkpoint = resume_from_checkpoint
        self.terminate_on_nan = terminate_on_nan
        self.shown_warnings = set()

        self.fast_dev_run = fast_dev_run
        if self.fast_dev_run:
            self.num_sanity_val_steps = 0
            self.max_epochs = 1
            log.info('Running in fast_dev_run mode: will run a full train,'
                     ' val and test loop using a single batch')

        # set default save path if user didn't provide one
        self.default_root_dir = default_root_dir

        # Backward compatibility, TODO: remove in v0.8.0
        if default_save_path is not None:
            self.default_root_dir = default_save_path

        if self.default_root_dir is None:
            self.default_root_dir = os.getcwd()

        # training bookeeping
        self.total_batch_idx = 0
        self.running_loss = TensorRunningAccum(window_length=20)
        self.batch_idx = 0
        self.tqdm_metrics = {}
        self.callback_metrics = {}
        self.num_val_batches = 0
        self.num_training_batches = 0
        self.num_test_batches = 0
        self.train_dataloader = None
        self.test_dataloaders = None
        self.val_dataloaders = None

        # training state
        self.model = None
        self.testing = False
        self.disable_validation = False
        self.lr_schedulers = []
        self.optimizers = None
        self.optimizer_frequencies = []
        self.global_step = 0
        self.current_epoch = 0
        self.total_batches = 0
        self.interrupted = False

        # configure logger
        self.configure_logger(logger)

        # configure profiler
        if profiler is True:
            profiler = SimpleProfiler()
        self.profiler = profiler or PassThroughProfiler()

        # configure early stop callback
        # creates a default one if none passed in
        self.configure_early_stopping(early_stop_callback)

        # configure checkpoint callback
        self.checkpoint_callback = checkpoint_callback
        self.weights_save_path = weights_save_path

        # accumulated grads
        self.accumulate_grad_batches = accumulate_grad_batches
        self.configure_accumulated_gradients(accumulate_grad_batches)

        # for gpus allow int, string and gpu list
        if auto_select_gpus and isinstance(gpus, int):
            self.gpus = pick_multiple_gpus(gpus)
        else:
            self.gpus = gpus

        self.data_parallel_device_ids = parse_gpu_ids(self.gpus)
        self.root_gpu = determine_root_gpu_device(self.data_parallel_device_ids)
        self.root_device = torch.device("cpu")

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
            self.current_tpu_idx = None

        # init flags for SLURM+ddp to work
        self.proc_rank = 0
        self.world_size = 1
        self.node_rank = 0
        self.configure_slurm_ddp(self.num_nodes)

        # nvidia setup
        self.set_nvidia_flags(self.is_slurm_managing_tasks, self.data_parallel_device_ids)

        # can't init progress bar here because starting a new process
        # means the progress_bar won't survive pickling
        # backward compatibility
        if show_progress_bar is not None:
            self.show_progress_bar = show_progress_bar

        # logging
        self.log_save_interval = log_save_interval
        self.val_check_interval = val_check_interval

        # backward compatibility
        if add_row_log_interval is not None:
            rank_zero_warn("`add_row_log_interval` has renamed to `row_log_interval` since v0.5.0"
                           " and this method will be removed in v0.8.0", DeprecationWarning)
            if not row_log_interval:  # in case you did not set the proper value
                row_log_interval = add_row_log_interval
        self.row_log_interval = row_log_interval

        # how much of the data to use
        self.overfit_pct = overfit_pct
        self.determine_data_use_amount(train_percent_check, val_percent_check,
                                       test_percent_check, overfit_pct)

        # 16 bit mixed precision training using apex
        self.amp_level = amp_level
        self.precision = precision

        # Backward compatibility, TODO: remove in v0.9.0
        if use_amp is not None:
            rank_zero_warn("`use_amp` has been replaced by `precision` since v0.7.0"
                           " and this argument will be removed in v0.9.0", DeprecationWarning)
            self.precision = 16 if use_amp else 32

        assert self.precision in (16, 32), 'only 32 or 16 bit precision supported'

        if self.precision == 16 and self.num_tpu_cores is None:
            use_amp = True
        self.init_amp(use_amp)

        # Callback system
        self.on_init_end()