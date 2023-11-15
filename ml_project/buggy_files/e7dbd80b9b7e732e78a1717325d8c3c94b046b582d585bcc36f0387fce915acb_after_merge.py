    def apply(self, func, *args, **kwargs):
        return self._apply_agg_function(
            # Grouping column in never dropped in groupby.apply, so drop=False
            lambda df: df.apply(func, *args, **kwargs),
            drop=False,
        )