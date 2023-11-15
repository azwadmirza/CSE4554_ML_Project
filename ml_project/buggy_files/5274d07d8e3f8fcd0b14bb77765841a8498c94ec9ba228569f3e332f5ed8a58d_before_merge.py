def align_diff_index_ops(func, this_index_ops: "IndexOpsMixin", *args) -> "IndexOpsMixin":
    """
    Align the `IndexOpsMixin` objects and apply the function.

    Parameters
    ----------
    func : The function to apply
    this_index_ops : IndexOpsMixin
        A base `IndexOpsMixin` object
    args : list of other arguments including other `IndexOpsMixin` objects

    Returns
    -------
    `Index` if all `this_index_ops` and arguments are `Index`; otherwise `Series`
    """
    from databricks.koalas.indexes import Index
    from databricks.koalas.series import Series, first_series

    cols = [arg for arg in args if isinstance(arg, IndexOpsMixin)]

    if isinstance(this_index_ops, Series) and all(isinstance(col, Series) for col in cols):
        combined = combine_frames(this_index_ops.to_frame(), *cols, how="full")

        return column_op(func)(
            combined["this"]._kser_for(combined["this"]._internal.column_labels[0]),
            *[
                combined["that"]._kser_for(label)
                for label in combined["that"]._internal.column_labels
            ]
        )
    else:
        # This could cause as many counts, reset_index calls, joins for combining
        # as the number of `Index`s in `args`. So far it's fine since we can assume the ops
        # only work between at most two `Index`s. We might need to fix it in the future.

        self_len = len(this_index_ops)
        if any(len(col) != self_len for col in args if isinstance(col, IndexOpsMixin)):
            raise ValueError("operands could not be broadcast together with shapes")

        with option_context("compute.default_index_type", "distributed-sequence"):
            if isinstance(this_index_ops, Index) and all(isinstance(col, Index) for col in cols):
                return (
                    cast(
                        Series,
                        column_op(func)(
                            this_index_ops.to_series().reset_index(drop=True),
                            *[
                                arg.to_series().reset_index(drop=True)
                                if isinstance(arg, Index)
                                else arg
                                for arg in args
                            ]
                        ),
                    )
                    .sort_index()
                    .to_frame(DEFAULT_SERIES_NAME)
                    .set_index(DEFAULT_SERIES_NAME)
                    .index.rename(this_index_ops.name)
                )
            elif isinstance(this_index_ops, Series):
                this = this_index_ops.reset_index()
                that = [
                    cast(Series, col.to_series() if isinstance(col, Index) else col).reset_index(
                        drop=True
                    )
                    for col in cols
                ]

                combined = combine_frames(this, *that, how="full").sort_index()
                combined = combined.set_index(
                    combined._internal.column_labels[: this_index_ops._internal.index_level]
                )
                combined.index.names = this_index_ops._internal.index_names

                return column_op(func)(
                    first_series(combined["this"]),
                    *[
                        combined["that"]._kser_for(label)
                        for label in combined["that"]._internal.column_labels
                    ]
                )
            else:
                this = cast(Index, this_index_ops).to_frame().reset_index(drop=True)

                that_series = next(col for col in cols if isinstance(col, Series))
                that_frame = that_series._kdf[
                    [col.to_series() if isinstance(col, Index) else col for col in cols]
                ]

                combined = combine_frames(this, that_frame.reset_index()).sort_index()

                self_index = (
                    combined["this"].set_index(combined["this"]._internal.column_labels).index
                )

                other = combined["that"].set_index(
                    combined["that"]._internal.column_labels[: that_series._internal.index_level]
                )
                other.index.names = that_series._internal.index_names

                return column_op(func)(
                    self_index, *[other._kser_for(label) for label in other._internal.column_labels]
                )