def execute_sort_values(data, op, inplace=None, by=None):
    if inplace is None:
        inplace = op.inplace
    # ignore_index is new in Pandas version 1.0.0.
    ignore_index = getattr(op, 'ignore_index', False)
    if isinstance(data, (pd.DataFrame, pd.Series)):
        kwargs = dict(axis=op.axis, ascending=op.ascending, ignore_index=ignore_index,
                      na_position=op.na_position, kind=op.kind)
        if isinstance(data, pd.DataFrame):
            kwargs['by'] = by if by is not None else op.by
        if inplace:
            kwargs['inplace'] = True
            try:
                data.sort_values(**kwargs)
            except TypeError:  # pragma: no cover
                kwargs.pop('ignore_index', None)
                data.sort_values(**kwargs)
            return data
        else:
            try:
                return data.sort_values(**kwargs)
            except TypeError:  # pragma: no cover
                kwargs.pop('ignore_index', None)
                return data.sort_values(**kwargs)

    else:  # pragma: no cover
        # cudf doesn't support axis and kind
        if isinstance(data, cudf.DataFrame):
            return data.sort_values(
                op.by, ascending=op.ascending, na_position=op.na_position)
        else:
            return data.sort_values(
                ascending=op.ascending, na_position=op.na_position)