    def __init__(self, **kwargs):
        self._plasma_store = None

        self._storage_manager_ref = None
        self._shared_holder_ref = None
        self._task_queue_ref = None
        self._mem_quota_ref = None
        self._dispatch_ref = None
        self._events_ref = None
        self._status_ref = None
        self._execution_ref = None
        self._daemon_ref = None
        self._receiver_manager_ref = None

        self._cluster_info_ref = None
        self._cpu_calc_actors = []
        self._inproc_holder_actors = []
        self._inproc_io_runner_actors = []
        self._cuda_calc_actors = []
        self._cuda_holder_actors = []
        self._sender_actors = []
        self._receiver_actors = []
        self._spill_actors = []
        self._process_helper_actors = []
        self._result_sender_ref = None

        self._advertise_addr = kwargs.pop('advertise_addr', None)

        cuda_devices = kwargs.pop('cuda_devices', None) or os.environ.get('CUDA_VISIBLE_DEVICES')
        if not cuda_devices:
            self._n_cuda_process = 0
        else:
            cuda_devices = os.environ['CUDA_VISIBLE_DEVICES'] = ','.join(str(d) for d in cuda_devices)
            if cuda_devices:
                logger.info('Started Mars worker with CUDA cards %s', cuda_devices)
            self._n_cuda_process = resource.cuda_count()

        self._n_cpu_process = int(kwargs.pop('n_cpu_process', None) or resource.cpu_count())
        self._n_net_process = int(kwargs.pop('n_net_process', None) or '4')

        self._spill_dirs = kwargs.pop('spill_dirs', None)
        if self._spill_dirs:
            if isinstance(self._spill_dirs, str):
                from .utils import parse_spill_dirs
                self._spill_dirs = options.worker.spill_directory = parse_spill_dirs(self._spill_dirs)
            else:
                options.worker.spill_directory = self._spill_dirs
        else:
            self._spill_dirs = options.worker.spill_directory = []

        options.worker.disk_compression = kwargs.pop('disk_compression', None) or \
            options.worker.disk_compression
        options.worker.transfer_compression = kwargs.pop('transfer_compression', None) or \
            options.worker.transfer_compression
        options.worker.io_parallel_num = kwargs.pop('io_parallel_num', None) or False
        options.worker.recover_dead_process = not (kwargs.pop('disable_proc_recover', None) or False)

        self._total_mem = kwargs.pop('total_mem', None)
        self._cache_mem_limit = kwargs.pop('cache_mem_limit', None)
        self._soft_mem_limit = kwargs.pop('soft_mem_limit', None) or '80%'
        self._hard_mem_limit = kwargs.pop('hard_mem_limit', None) or '90%'
        self._ignore_avail_mem = kwargs.pop('ignore_avail_mem', None) or False
        self._min_mem_size = kwargs.pop('min_mem_size', None) or 128 * 1024 ** 2

        self._plasma_dir = kwargs.pop('plasma_dir', None)
        self._use_ext_plasma_dir = kwargs.pop('use_ext_plasma_dir', None) or False

        self._soft_quota_limit = self._soft_mem_limit

        self._calc_memory_limits()

        if kwargs:  # pragma: no cover
            raise TypeError('Keyword arguments %r cannot be recognized.' % ', '.join(kwargs))