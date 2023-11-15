    def __init__(self, values, index, level=-1, value_columns=None,
                 fill_value=None, constructor=None):

        self.is_categorical = None
        self.is_sparse = is_sparse(values)
        if values.ndim == 1:
            if isinstance(values, Categorical):
                self.is_categorical = values
                values = np.array(values)
            elif self.is_sparse:
                # XXX: Makes SparseArray *dense*, but it's supposedly
                # a single column at a time, so it's "doable"
                values = values.values
            values = values[:, np.newaxis]
        self.values = values
        self.value_columns = value_columns
        self.fill_value = fill_value

        if constructor is None:
            if self.is_sparse:
                self.constructor = SparseDataFrame
            else:
                self.constructor = DataFrame
        else:
            self.constructor = constructor

        if value_columns is None and values.shape[1] != 1:  # pragma: no cover
            raise ValueError('must pass column labels for multi-column data')

        self.index = index

        self.level = self.index._get_level_number(level)

        # when index includes `nan`, need to lift levels/strides by 1
        self.lift = 1 if -1 in self.index.labels[self.level] else 0

        self.new_index_levels = list(index.levels)
        self.new_index_names = list(index.names)

        self.removed_name = self.new_index_names.pop(self.level)
        self.removed_level = self.new_index_levels.pop(self.level)

        self._make_sorted_values_labels()
        self._make_selectors()