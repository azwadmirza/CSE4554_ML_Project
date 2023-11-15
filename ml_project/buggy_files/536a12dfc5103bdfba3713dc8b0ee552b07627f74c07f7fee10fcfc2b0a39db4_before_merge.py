    def _get_join_indexers(self):
        """ return the join indexers """

        def flip(xs):
            """ unlike np.transpose, this returns an array of tuples """
            labels = list(string.ascii_lowercase[: len(xs)])
            dtypes = [x.dtype for x in xs]
            labeled_dtypes = list(zip(labels, dtypes))
            return np.array(list(zip(*xs)), labeled_dtypes)

        # values to compare
        left_values = (
            self.left.index.values if self.left_index else self.left_join_keys[-1]
        )
        right_values = (
            self.right.index.values if self.right_index else self.right_join_keys[-1]
        )
        tolerance = self.tolerance

        # we require sortedness and non-null values in the join keys
        msg_sorted = "{side} keys must be sorted"
        msg_missings = "Merge keys contain null values on {side} side"

        if not Index(left_values).is_monotonic:
            if isnull(left_values).any():
                raise ValueError(msg_missings.format(side="left"))
            else:
                raise ValueError(msg_sorted.format(side="left"))

        if not Index(right_values).is_monotonic:
            if isnull(right_values).any():
                raise ValueError(msg_missings.format(side="right"))
            else:
                raise ValueError(msg_sorted.format(side="right"))

        # initial type conversion as needed
        if needs_i8_conversion(left_values):
            left_values = left_values.view("i8")
            right_values = right_values.view("i8")
            if tolerance is not None:
                tolerance = tolerance.value

        # a "by" parameter requires special handling
        if self.left_by is not None:
            # remove 'on' parameter from values if one existed
            if self.left_index and self.right_index:
                left_by_values = self.left_join_keys
                right_by_values = self.right_join_keys
            else:
                left_by_values = self.left_join_keys[0:-1]
                right_by_values = self.right_join_keys[0:-1]

            # get tuple representation of values if more than one
            if len(left_by_values) == 1:
                left_by_values = left_by_values[0]
                right_by_values = right_by_values[0]
            else:
                left_by_values = flip(left_by_values)
                right_by_values = flip(right_by_values)

            # upcast 'by' parameter because HashTable is limited
            by_type = _get_cython_type_upcast(left_by_values.dtype)
            by_type_caster = _type_casters[by_type]
            left_by_values = by_type_caster(left_by_values)
            right_by_values = by_type_caster(right_by_values)

            # choose appropriate function by type
            func = _asof_by_function(self.direction)
            return func(
                left_values,
                right_values,
                left_by_values,
                right_by_values,
                self.allow_exact_matches,
                tolerance,
            )
        else:
            # choose appropriate function by type
            func = _asof_function(self.direction)
            return func(left_values, right_values, self.allow_exact_matches, tolerance)