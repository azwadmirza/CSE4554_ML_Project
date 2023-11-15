def align_diff_series(func, this_series, *args, how="full"):
    from databricks.koalas.base import IndexOpsMixin
    from databricks.koalas.series import Series

    cols = [arg for arg in args if isinstance(arg, IndexOpsMixin)]
    combined = combine_frames(this_series.to_frame(), *cols, how=how)

    that_columns = [
        combined["that"][arg._internal.column_labels[0]]._scol
        if isinstance(arg, IndexOpsMixin)
        else arg
        for arg in args
    ]

    scol = func(combined["this"][this_series._internal.column_labels[0]]._scol, *that_columns)

    return Series(
        combined._internal.copy(scol=scol, column_labels=this_series._internal.column_labels),
        anchor=combined,
    )