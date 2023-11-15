    def size(self):
        if self._axis == 0:
            if self._as_index:
                work_object = self[self._df.columns[0]]
            else:
                # Size always works in as_index=True mode so it is necessary to make a copy
                # of _kwargs and change as_index in it
                kwargs = self._kwargs.copy()
                kwargs["as_index"] = True
                kwargs["squeeze"] = True
                work_object = SeriesGroupBy(
                    self._df[self._df.columns[0]],
                    self._by,
                    self._axis,
                    idx_name=self._idx_name,
                    drop=False,
                    **kwargs,
                )

            result = work_object._groupby_reduce(
                lambda df: pandas.DataFrame(df.size()),
                lambda df: df.sum(),
                numeric_only=False,
            )
            series_result = Series(query_compiler=result._query_compiler)
            # Pandas does not name size() output
            series_result.name = None
            return series_result
        else:
            return DataFrameGroupBy(
                self._df.T,
                self._by,
                0,
                drop=self._drop,
                idx_name=self._idx_name,
                **self._kwargs,
            ).size()