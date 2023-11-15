def _worker_reset_iterator(
    is_train: bool, cyclic: bool, cycle_num: int,
):
    """Initialize or reset iterators of workers."""

    _WorkerData.dataset_iterator = _sequential_sample_generator(
        dataset=_WorkerData.dataset,
        transformation=_WorkerData.transformation,
        is_train=is_train,
        cyclic=cyclic,
    )
    assert isinstance(_WorkerData.iterator_latest_reset_cycle, int)
    _WorkerData.iterator_latest_reset_cycle = cycle_num
    _WorkerData.iterator_exhausted_indicator = False