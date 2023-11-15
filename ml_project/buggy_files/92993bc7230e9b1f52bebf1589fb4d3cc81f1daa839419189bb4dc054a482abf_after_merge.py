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