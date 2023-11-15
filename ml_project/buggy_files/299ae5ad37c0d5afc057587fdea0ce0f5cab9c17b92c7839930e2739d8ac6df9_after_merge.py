    def __init__(self, model, prefix="auto", init_loc_fn=init_to_median, rank=1):
        if not isinstance(rank, numbers.Number) or not rank > 0:
            raise ValueError("Expected rank > 0 but got {}".format(rank))
        self.rank = rank
        super(AutoLowRankMultivariateNormal, self).__init__(
            model, prefix=prefix, init_loc_fn=init_loc_fn)