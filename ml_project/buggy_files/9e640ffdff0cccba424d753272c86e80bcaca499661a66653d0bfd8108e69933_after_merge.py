    def fetch(self, session=None, **kw):
        from .indexing.iloc import DataFrameIlocGetItem, SeriesIlocGetItem

        batch_size = kw.pop('batch_size', 1000)
        if len(kw) > 0:  # pragma: no cover
            raise TypeError(
                f"'{next(iter(kw))}' is an invalid keyword argument for this function")

        if isinstance(self.op, (DataFrameIlocGetItem, SeriesIlocGetItem)):
            # see GH#1871
            # already iloc, do not trigger batch fetch
            return self._fetch(session=session, **kw)
        else:
            batches = list(self._iter(batch_size=batch_size, session=session))
            return pd.concat(batches) if len(batches) > 1 else batches[0]