def _worker_initializer(
    dataset: Dataset,
    dataset_len: int,
    num_workers: int,
    transformation: Transformation,
    cyclic: bool,
    worker_id_queue: Queue,
):
    """Initialier for processing pool."""

    global _worker_dataset
    global _worker_dataset_iterator
    global _worker_transformation
    global _worker_iterator_latest_reset_cycle
    global _worker_iterator_exhausted_indicator

    # dataset replica
    _worker_dataset = dataset
    # current dataset iterator in form of a transformation applied to the dataset
    _worker_dataset_iterator = None
    # replicate transformation
    _worker_transformation = transformation
    # indicates which cycle the iterator has been reset last
    _worker_iterator_latest_reset_cycle = 0
    # indicates whether the iterator was previously depleted
    _worker_iterator_exhausted_indicator = None

    # get unique worker id
    worker_id = int(worker_id_queue.get())
    multiprocessing.current_process().name = f"worker_{worker_id}"

    # propagate worker information
    MPWorkerInfo.set_worker_info(num_workers=num_workers, worker_id=worker_id)