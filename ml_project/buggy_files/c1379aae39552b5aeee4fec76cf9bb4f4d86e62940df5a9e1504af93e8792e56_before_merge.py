    def _map_series_op(self, op, other):
        if isinstance(other, DataFrame) or is_sequence(other):
            raise ValueError(
                "%s with another DataFrame or a sequence is currently not supported; "
                "however, got %s." % (op, type(other)))

        applied = []
        for column in self._internal.data_columns:
            applied.append(getattr(self[column], op)(other))

        sdf = self._sdf.select(
            self._internal.index_columns + [c._scol for c in applied])
        internal = self._internal.copy(sdf=sdf, data_columns=[c.name for c in applied])
        return DataFrame(internal)