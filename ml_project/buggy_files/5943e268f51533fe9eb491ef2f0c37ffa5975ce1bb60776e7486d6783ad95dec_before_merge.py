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
        assert isinstance(
            by, type(self)
        ), "Can only use groupby reduce with another Query Compiler"

        other_len = len(by.columns)
        as_index = groupby_args.get("as_index", True)

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
            return result.reset_index(drop=False)

        if reduce_func is not None:

            def _reduce(df):
                # See note above about setting `as_index`
                groupby_args["as_index"] = True
                if other_len > 1:
                    by = list(df.columns[0:other_len])
                else:
                    by = df.columns[0]
                result = reduce_func(
                    df.groupby(by=by, axis=axis, **groupby_args), **reduce_args
                )
                if (
                    not isinstance(result.index, pandas.MultiIndex)
                    and result.index.name is not None
                    and "_modin_groupby_" in result.index.name
                ):
                    result.index.name = result.index.name[len("_modin_groupby_") :]
                return result

        else:

            def _reduce(df):
                # See note above about setting `as_index`
                groupby_args["as_index"] = True
                if other_len > 1:
                    by = list(df.columns[0:other_len])
                else:
                    by = df.columns[0]
                result = map_func(
                    df.groupby(by=by, axis=axis, **groupby_args), **map_args
                )
                if (
                    not isinstance(result.index, pandas.MultiIndex)
                    and result.index.name is not None
                    and "_modin_groupby_" in result.index.name
                ):
                    result.index.name = result.index.name[len("_modin_groupby_") :]
                return result

        if axis == 0:
            new_columns = (
                self.columns
                if not numeric_only
                else self._modin_frame._numeric_columns(True)
            )
            new_index = None
            compute_qc = (
                self.getitem_column_array(new_columns) if numeric_only else self
            )
        else:
            new_index = self.index
            new_columns = None
            compute_qc = self
        new_modin_frame = compute_qc._modin_frame.groupby_reduce(
            axis,
            by._modin_frame,
            _map,
            _reduce,
            new_columns=new_columns,
            new_index=new_index,
        )
        result = self.__constructor__(new_modin_frame)
        # Reset `as_index` because it was edited inplace.
        groupby_args["as_index"] = as_index
        if as_index:
            return result
        else:
            if result.index.name is None or result.index.name in result.columns:
                drop = False
            return result.reset_index(drop=not drop)