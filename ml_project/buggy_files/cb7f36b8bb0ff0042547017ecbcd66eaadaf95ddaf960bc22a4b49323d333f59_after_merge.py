    def __init__(
        self,
        dataset: Dataset,
        transformation: Transformation,
        cyclic: bool,
        is_train: bool,
        batch_size: int,
        shuffle: bool = False,
        batchify_fn: Callable = None,
        ctx: mx.Context = None,
        dtype: DType = np.float32,
        num_prefetch: Optional[int] = None,
        num_workers: Optional[int] = None,
    ):
        # Some windows error with the ForkingPickler prevents usage currently:
        if sys.platform == "win32":
            logging.warning(
                "You have set `num_workers` for to a non zero value, "
                "however, currently multiprocessing is not supported on windows."
            )
            num_workers = 0

        self.dataset = dataset
        self.dataset_len = None
        if isinstance(dataset, Sized):
            assert isinstance(dataset, Sized)
            self.dataset_len = len(dataset)
        else:
            self.dataset_len = len(list(dataset))
        # indicates that we want to cycle through the dataset
        self.cyclic = cyclic
        # indicates the current cycle, needed for resetting iterators at each cycle
        self.cycle_num = 0

        self.dtype = dtype
        self.is_train = is_train
        self.transformation = transformation
        self.ctx = ctx
        self.batch_size = batch_size
        self.shuffle = shuffle

        assert (
            num_workers is None or num_workers <= self.dataset_len
        ), "Cannot have more workers than dataset entries currently."

        # TODO: switch to default multiprocessing.cpu_count() here
        default_num_workers = 0
        self.num_workers = max(
            0,
            num_workers
            if num_workers is not None
            else min(self.dataset_len, default_num_workers),
        )
        self.num_prefetch = max(
            0,
            num_prefetch if num_prefetch is not None else 2 * self.num_workers,
        )
        self.worker_pool = None
        # In order to set unique IDs to workers:
        self.worker_manager = None
        self.worker_id_queue = None
        # In order to recycle unused but pre-calculated batches from last epoch for training:
        self.multi_worker_cache = None

        if self.num_workers > 0:
            # generate unique ids for processes
            self.worker_manager = multiprocessing.Manager()
            self.worker_id_queue = self.worker_manager.Queue()
            for i in range(self.num_workers):
                self.worker_id_queue.put(i)

            self.worker_pool = multiprocessing.get_context("spawn").Pool(
                self.num_workers,
                initializer=_worker_initializer,
                initargs=[
                    self.dataset,
                    self.transformation,
                    self.num_workers,
                    self.worker_id_queue,
                ],
            )

        if batchify_fn is None:
            self.batchify_fn = default_batchify_fn
        else:
            self.batchify_fn = batchify_fn