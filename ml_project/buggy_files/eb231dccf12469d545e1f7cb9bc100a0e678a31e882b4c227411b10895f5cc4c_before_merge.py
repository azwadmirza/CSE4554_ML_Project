    def _cum(self, func, skipna: bool):
        # This is used for cummin, cummax, cumxum, etc.
        if func == F.min:
            func = "cummin"
        elif func == F.max:
            func = "cummax"
        elif func == F.sum:
            func = "cumsum"
        elif func.__name__ == "cumprod":
            func = "cumprod"

        if len(self._internal.index_columns) == 0:
            raise ValueError("Index must be set.")

        applied = []
        for column in self._internal.data_columns:
            applied.append(getattr(self[column], func)(skipna))

        sdf = self._sdf.select(
            self._internal.index_columns + [c._scol for c in applied])
        internal = self._internal.copy(sdf=sdf, data_columns=[c.name for c in applied])
        return DataFrame(internal)