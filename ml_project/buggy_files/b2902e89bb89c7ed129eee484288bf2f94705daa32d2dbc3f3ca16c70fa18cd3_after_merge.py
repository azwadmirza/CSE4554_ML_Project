def _worker_initializer(
    dataset: Dataset,
    transformation: Transformation,
    num_workers: int,
    worker_id_queue: Queue,
):
    """Initialier for processing pool."""

    _WorkerData.dataset = dataset
    _WorkerData.transformation = transformation

    # get unique worker id
    worker_id = int(worker_id_queue.get())
    multiprocessing.current_process().name = f"worker_{worker_id}"

    # propagate worker information
    MPWorkerInfo.set_worker_info(
        num_workers=num_workers, worker_id=worker_id, worker_process=True
    )