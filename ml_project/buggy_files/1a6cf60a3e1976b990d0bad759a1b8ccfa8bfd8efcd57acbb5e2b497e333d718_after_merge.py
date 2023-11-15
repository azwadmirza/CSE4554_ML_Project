def combine_frames(this, *args, how="full"):
    """
    This method combines `this` DataFrame with a different `that` DataFrame or
    Series from a different DataFrame.

    It returns a DataFrame that has prefix `this_` and `that_` to distinct
    the columns names from both DataFrames

    It internally performs a join operation which can be expensive in general.
    So, if `compute.ops_on_diff_frames` option is False,
    this method throws an exception.
    """
    from databricks.koalas import Series
    from databricks.koalas import DataFrame
    from databricks.koalas.config import get_option

    if all(isinstance(arg, Series) for arg in args):
        assert all(arg._kdf is args[0]._kdf for arg in args), \
            "Currently only one different DataFrame (from given Series) is supported"
        if this is args[0]._kdf:
            return  # We don't need to combine. All series is in this.
        that = args[0]._kdf[list(args)]
    elif len(args) == 1 and isinstance(args[0], DataFrame):
        assert isinstance(args[0], DataFrame)
        if this is args[0]:
            return  # We don't need to combine. `this` and `that` are same.
        that = args[0]
    else:
        raise AssertionError("args should be single DataFrame or "
                             "single/multiple Series")

    if get_option("compute.ops_on_diff_frames"):
        this_index_map = this._internal.index_map
        that_index_map = that._internal.index_map
        assert len(this_index_map) == len(that_index_map)

        join_scols = []
        merged_index_scols = []

        # If the same named index is found, that's used.
        for this_column, this_name in this_index_map:
            for that_col, that_name in that_index_map:
                if this_name == that_name:
                    # We should merge the Spark columns into one
                    # to mimic pandas' behavior.
                    this_scol = this._internal.scol_for(this_column)
                    that_scol = that._internal.scol_for(that_col)
                    join_scol = this_scol == that_scol
                    join_scols.append(join_scol)
                    merged_index_scols.append(
                        F.when(
                            this_scol.isNotNull(), this_scol
                        ).otherwise(that_scol).alias(this_column))
                    break
            else:
                raise ValueError("Index names must be exactly matched currently.")

        assert len(join_scols) > 0, "cannot join with no overlapping index names"

        joined_df = this._sdf.alias("this").join(
            that._sdf.alias("that"), on=join_scols, how=how)

        joined_df = joined_df.select(
            merged_index_scols +
            [this[idx]._scol.alias("__this_%s" % this._internal.column_name_for(idx))
             for idx in this._internal.column_index] +
            [that[idx]._scol.alias("__that_%s" % that._internal.column_name_for(idx))
             for idx in that._internal.column_index])

        index_columns = set(this._internal.index_columns)
        new_data_columns = [c for c in joined_df.columns if c not in index_columns]
        level = max(this._internal.column_index_level, that._internal.column_index_level)
        column_index = ([tuple(['this'] + ([''] * (level - len(idx))) + list(idx))
                         for idx in this._internal.column_index]
                        + [tuple(['that'] + ([''] * (level - len(idx))) + list(idx))
                           for idx in that._internal.column_index])
        column_index_names = ((([None] * (1 + level - len(this._internal.column_index_level)))
                               + this._internal.column_index_names)
                              if this._internal.column_index_names is not None else None)
        return DataFrame(
            this._internal.copy(sdf=joined_df, data_columns=new_data_columns,
                                column_index=column_index, column_index_names=column_index_names))
    else:
        raise ValueError(
            "Cannot combine the series or dataframe because it comes from a different dataframe. "
            "In order to allow this operation, enable 'compute.ops_on_diff_frames' option.")