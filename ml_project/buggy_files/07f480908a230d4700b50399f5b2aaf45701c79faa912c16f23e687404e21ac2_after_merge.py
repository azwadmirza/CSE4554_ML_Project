    def caller(self, *args, **kwargs):
        # If `numeric_only` is None then we don't know what columns/indices will
        # be dropped at the result of reduction function, and so can't preserve labels
        preserve_index = kwargs.get("numeric_only", None) is not None
        return applier.register(*funcs, preserve_index=preserve_index)(
            self, *args, **kwargs
        )