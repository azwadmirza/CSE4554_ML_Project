def align_diff_series(func, this_series, *args, how="full"):
    from databricks.koalas.base import IndexOpsMixin
    from databricks.koalas.series import Series

    cols = [arg for arg in args if isinstance(arg, IndexOpsMixin)]
    combined = combine_frames(this_series.to_frame(), *cols, how=how)

    scol = func(
        combined["this"]._internal.column_scols[0], *combined["that"]._internal.column_scols
    )

    return Series(
        combined._internal.copy(scol=scol, column_labels=this_series._internal.column_labels),
        anchor=combined,
    )