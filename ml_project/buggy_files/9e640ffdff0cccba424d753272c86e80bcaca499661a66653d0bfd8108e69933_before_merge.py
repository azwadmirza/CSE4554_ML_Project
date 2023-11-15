    def fetch(self, session=None, **kw):
        batch_size = kw.pop('batch_size', 1000)
        if len(kw) > 0:  # pragma: no cover
            raise TypeError(
                f"'{next(iter(kw))}' is an invalid keyword argument for this function")
        batches = list(self._iter(batch_size=batch_size, session=session))
        return pd.concat(batches) if len(batches) > 1 else batches[0]