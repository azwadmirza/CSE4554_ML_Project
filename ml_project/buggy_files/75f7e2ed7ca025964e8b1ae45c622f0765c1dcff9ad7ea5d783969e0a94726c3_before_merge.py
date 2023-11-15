    def __init__(self, lock_free=False, dispatched=True):
        super().__init__()
        self._work_items = deque()
        self._max_work_item_id = 0
        self._cur_work_items = dict()

        self._lock_free = lock_free or options.worker.lock_free_fileio
        self._lock_work_items = dict()

        self._dispatched = dispatched