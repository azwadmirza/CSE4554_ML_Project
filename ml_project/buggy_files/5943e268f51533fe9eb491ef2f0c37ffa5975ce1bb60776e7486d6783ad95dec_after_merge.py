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
        first_column = qc.columns[0]
        as_index = groupby_args.get("as_index", True)
        # When drop is False and as_index is False, we do not want to insert the `by`
        # data as a new column in the dataframe. We will drop it.
        drop_by = not drop

        # For simplicity we allow only one function to be passed in if both are the
        # same.
        if reduce_func is None:
            reduce_func = map_func
            reduce_args = map_args

        def _map(df, other):
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
            if (
                not isinstance(result.index, pandas.MultiIndex)
                and result.index.name is not None
                and result.index.name in result.columns
            ):
                result.index.name = "{}{}".format("_modin_groupby_", result.index.name)
            return result

        def _reduce(df):
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
            # Avoid inserting data after the first partition or if the data did not come
            # from this query compiler.
            if not as_index and (first_column not in df.columns or drop_by):
                return result.drop(columns=by_part)
            return result

        if axis == 0:
            if not as_index and drop:
                new_columns = by.columns.append(qc.columns)
            else:
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