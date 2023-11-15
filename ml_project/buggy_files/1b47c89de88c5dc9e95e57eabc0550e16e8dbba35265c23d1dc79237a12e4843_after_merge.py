    def __init__(
        self,
        multioutput: str = 'uniform_average',
        compute_on_step: bool = True,
        dist_sync_on_step: bool = False,
        process_group: Optional[Any] = None,
        dist_sync_fn: Callable = None,
    ):
        super().__init__(
            compute_on_step=compute_on_step,
            dist_sync_on_step=dist_sync_on_step,
            process_group=process_group,
            dist_sync_fn=dist_sync_fn,
        )
        allowed_multioutput = ('raw_values', 'uniform_average', 'variance_weighted')
        if multioutput not in allowed_multioutput:
            raise ValueError(
                f'Invalid input to argument `multioutput`. Choose one of the following: {allowed_multioutput}'
            )
        self.multioutput = multioutput
        self.add_state("y", default=[], dist_reduce_fx=None)
        self.add_state("y_pred", default=[], dist_reduce_fx=None)

        rank_zero_warn(
            'Metric `ExplainedVariance` will save all targets and'
            ' predictions in buffer. For large datasets this may lead'
            ' to large memory footprint.'
        )