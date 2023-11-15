    def columns(self, names):
        old_names = self._internal.data_columns
        if len(old_names) != len(names):
            raise ValueError(
                "Length mismatch: Expected axis has %d elements, new values have %d elements"
                % (len(old_names), len(names)))
        sdf = self._sdf.select(self._internal.index_scols +
                               [self[old_name]._scol.alias(new_name)
                                for (old_name, new_name) in zip(old_names, names)])
        self._internal = self._internal.copy(sdf=sdf, data_columns=names)