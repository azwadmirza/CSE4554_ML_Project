def _worker_reset_iterator(
    is_train: bool, cyclic: bool, cycle_num: int,
):
    """Initialize or reset iterators of workers."""

    global _worker_dataset
    global _worker_dataset_iterator
    global _worker_transformation
    global _worker_iterator_latest_reset_cycle
    global _worker_iterator_exhausted_indicator

    _worker_dataset_iterator = sequential_sample_generator(
        dataset=_worker_dataset,
        transformation=_worker_transformation,
        is_train=is_train,
        cyclic=cyclic,
    )
    assert isinstance(_worker_iterator_latest_reset_cycle, int)
    _worker_iterator_latest_reset_cycle = cycle_num
    _worker_iterator_exhausted_indicator = False