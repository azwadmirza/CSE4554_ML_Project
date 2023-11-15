    def __init__(
        self,
        dataset: Dataset,
        *,
        transform: Transformation,
        batch_size: int,
        ctx: mx.Context,
        num_workers: Optional[int] = None,
        num_prefetch: Optional[int] = None,
        dtype: DType = np.float32,
        **kwargs
    ) -> None:
        # TODO fix this bug:
        # Currently the is a bug with multi processing here,
        # see: _worker_fn in parallelized_loader.py for explanation
        if num_workers != 0 and num_workers is not None:
            logging.warning(
                "You have set `num_workers` for InferenceDataLoader to a non zero value, "
                "however, currently multiprocessing is not supported for the InferenceDataLoader."
            )
        num_workers = 0

        super().__init__(
            dataset=dataset,
            transform=transform,
            is_train=False,
            batch_size=batch_size,
            ctx=ctx,
            dtype=dtype,
            cyclic=False,
            num_workers=num_workers,
            num_prefetch=num_prefetch,
            **kwargs,
        )