def _worker_fn(
    batch_size: int,
    batchify_fn: Callable,
    dtype: DType,
    is_train: bool,
    shuffle: bool,
    cyclic: bool,
    cycle_num: int,
):
    """Function for processing data in worker process."""

    global _worker_dataset_iterator
    global _worker_iterator_latest_reset_cycle
    global _worker_iterator_exhausted_indicator

    # initialize, or reset the iterator at each cycle
    assert isinstance(_worker_iterator_latest_reset_cycle, int)
    if (_worker_iterator_latest_reset_cycle < cycle_num) and (
        _worker_iterator_latest_reset_cycle == 0 or not cyclic
    ):
        _worker_reset_iterator(is_train, cyclic, cycle_num)

    assert isinstance(
        _worker_dataset_iterator, Iterable
    ), f"Dataset not Iterable: {type(_worker_dataset_iterator)}."
    transformed_data = list(
        itertools.islice(_worker_dataset_iterator, batch_size)
    )

    if shuffle:
        random.shuffle(transformed_data)

    if transformed_data:
        success = True
        batch = batchify_fn(
            data=transformed_data, dtype=dtype, parallel_processing=True
        )
    else:
        # the second time without being able to provide a batch we want to delay calling them again
        # on fist exhaustion they should not be delayed, since they need to indicate depletion
        if _worker_iterator_exhausted_indicator:
            time.sleep(0.1)
        else:
            _worker_iterator_exhausted_indicator = True
        success = False
        batch = None

    buf = io.BytesIO()
    ForkingPickler(buf, pickle.HIGHEST_PROTOCOL).dump(
        (success, MPWorkerInfo.worker_id, batch)
    )
    return buf.getvalue()