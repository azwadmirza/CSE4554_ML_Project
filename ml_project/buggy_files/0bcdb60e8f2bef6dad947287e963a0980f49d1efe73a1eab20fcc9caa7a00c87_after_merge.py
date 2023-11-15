    def set_worker_info(
        cls, num_workers: int, worker_id: int, worker_process: bool
    ):
        cls.num_workers, cls.worker_id, cls.worker_process = (
            num_workers,
            worker_id,
            worker_process,
        )