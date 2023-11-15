def _as_in_context(batch: dict, ctx: mx.Context):
    """Move data into new context, should only be in main process."""
    assert (
        not MPWorkerInfo.worker_process
    ), "This function is not meant to be used in workers."
    batch = {
        k: v.as_in_context(ctx) if isinstance(v, nd.NDArray)
        # Workaround due to MXNet not being able to handle NDArrays with 0 in shape properly:
        else (
            stack(v, False, v.dtype, ctx)
            if isinstance(v[0], np.ndarray) and 0 in v[0].shape
            else v
        )
        for k, v in batch.items()
    }
    return batch