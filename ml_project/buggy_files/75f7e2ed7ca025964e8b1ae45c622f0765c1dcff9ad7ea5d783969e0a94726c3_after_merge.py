    def __init__(self, io_parallel_num=None, dispatched=True):
        super().__init__()
        self._work_items = deque()
        self._max_work_item_id = 0
        self._cur_work_items = dict()

        self._io_parallel_num = io_parallel_num or options.worker.io_parallel_num
        self._lock_work_items = dict()

        self._dispatched = dispatched