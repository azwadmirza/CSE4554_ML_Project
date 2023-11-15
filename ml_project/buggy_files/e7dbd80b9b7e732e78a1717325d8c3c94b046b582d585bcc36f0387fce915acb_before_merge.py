    def apply(self, func, *args, **kwargs):
        return self._apply_agg_function(
            lambda df: df.apply(func, *args, **kwargs), drop=self._as_index
        )