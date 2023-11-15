    def groupby_reduce(
        self,
        by,
        axis,
        groupby_args,
        map_func,
        map_args,
        reduce_func=None,
        reduce_args=None,
        numeric_only=True,
        drop=False,
    ):
        """Apply a Groupby via MapReduce pattern.

        Note: Result length will be the number of unique values in `by`.

        Currently, here is how this is implemented:
        - map phase:
            During the map phase we set `as_index` to True to force the `by` into the
            index for the next phase. We always do this so that the reduce phase has
            complete access of the `by` data without having to shuffle it twice. The map
            function is applied with the arguments provided. The `index` of the
            partitions will become the new `by` column. Sometimes, the name of `by` is
            the same as a data column. In these cases we add "_modin_groupby_" to the
            name of the index. This does not happen when grouping by multiple columns
            because those columns have already been dropped as a requirement.
        - reduce phase:
            During the reduce phase, the `by` data is moved from the `index` into the
            data. The names of those inserted become the `by` for the reduce phase of
            the groupby. Once applied, we drop the columns in all partitions after the
            first so we do not insert the data multiple times. We also avoid inserting
            data when the data from the `by` parameter did not come from this object.
            The columns can be derived externally but the new index must be computed
            post hoc.

        Args:
            by: The query compiler object to groupby.
            axis: The axis to groupby. Must be 0 currently.
            groupby_args: The arguments for the groupby component.
            map_func: The function to perform during the map phase.
            map_args: The arguments for the `map_func`.
            reduce_func: The function to perform during the reduce phase.
            reduce_args: The arguments for `reduce_func`.
            numeric_only: Whether to drop non-numeric columns.
            drop: Whether the data in `by` was dropped.

        Returns:
            A new Query Compiler
        """
        assert isinstance(
            by, type(self)
        ), "Can only use groupby reduce with another Query Compiler"
        assert axis == 0, "Can only groupby reduce with axis=0"

        if numeric_only:
            qc = self.getitem_column_array(self._modin_frame._numeric_columns(True))
        else:
            qc = self
        as_index = groupby_args.get("as_index", True)
        # For simplicity we allow only one function to be passed in if both are the
        # same.
        if reduce_func is None:
            reduce_func = map_func
            reduce_args = map_args

        def _map(df, other):
            def compute_map(df, other):
                # Set `as_index` to True to track the metadata of the grouping object
                # It is used to make sure that between phases we are constructing the
                # right index and placing columns in the correct order.
                groupby_args["as_index"] = True
                other = other.squeeze(axis=axis ^ 1)
                if isinstance(other, pandas.DataFrame):
                    df = pandas.concat(
                        [df] + [other[[o for o in other if o not in df]]], axis=1
                    )
                    other = list(other.columns)
                result = map_func(
                    df.groupby(by=other, axis=axis, **groupby_args), **map_args
                )
                # The _modin_groupby_ prefix indicates that this is the first partition,
                # and since we may need to insert the grouping data in the reduce phase
                if (
                    not isinstance(result.index, pandas.MultiIndex)
                    and result.index.name is not None
                    and result.index.name in result.columns
                ):
                    result.index.name = "{}{}".format(
                        "_modin_groupby_", result.index.name
                    )
                return result

            try:
                return compute_map(df, other)
            # This will happen with Arrow buffer read-only errors. We don't want to copy
            # all the time, so this will try to fast-path the code first.
            except (ValueError):
                return compute_map(df.copy(), other.copy())

        def _reduce(df):
            def compute_reduce(df):
                other_len = len(df.index.names)
                df = df.reset_index(drop=False)
                # See note above about setting `as_index`
                groupby_args["as_index"] = as_index
                if other_len > 1:
                    by_part = list(df.columns[0:other_len])
                else:
                    by_part = df.columns[0]
                result = reduce_func(
                    df.groupby(by=by_part, axis=axis, **groupby_args), **reduce_args
                )
                if (
                    not isinstance(result.index, pandas.MultiIndex)
                    and result.index.name is not None
                    and "_modin_groupby_" in result.index.name
                ):
                    result.index.name = result.index.name[len("_modin_groupby_") :]
                if isinstance(by_part, str) and by_part in result.columns:
                    if "_modin_groupby_" in by_part and drop:
                        col_name = by_part[len("_modin_groupby_") :]
                        new_result = result.drop(columns=col_name)
                        new_result.columns = [
                            col_name if "_modin_groupby_" in c else c
                            for c in new_result.columns
                        ]
                        return new_result
                    else:
                        return result.drop(columns=by_part)
                return result

            try:
                return compute_reduce(df)
            # This will happen with Arrow buffer read-only errors. We don't want to copy
            # all the time, so this will try to fast-path the code first.
            except (ValueError):
                return compute_reduce(df.copy())

        if axis == 0:
            new_columns = qc.columns
            new_index = None
        else:
            new_index = self.index
            new_columns = None
        new_modin_frame = qc._modin_frame.groupby_reduce(
            axis,
            by._modin_frame,
            _map,
            _reduce,
            new_columns=new_columns,
            new_index=new_index,
        )
        return self.__constructor__(new_modin_frame)