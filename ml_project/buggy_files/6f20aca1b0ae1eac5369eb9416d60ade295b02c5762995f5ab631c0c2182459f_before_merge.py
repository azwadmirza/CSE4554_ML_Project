        def caller(query_compiler, other, *args, **kwargs):
            axis = kwargs.get("axis", 0)
            broadcast = kwargs.pop("broadcast", False)
            if isinstance(other, type(query_compiler)):
                if broadcast:
                    assert (
                        len(other.columns) == 1
                    ), "Invalid broadcast argument for `broadcast_apply`, too many columns: {}".format(
                        len(other.columns)
                    )
                    # Transpose on `axis=1` because we always represent an individual
                    # column or row as a single-column Modin DataFrame
                    if axis == 1:
                        other = other.transpose()
                    return query_compiler.__constructor__(
                        query_compiler._modin_frame.broadcast_apply(
                            axis,
                            lambda l, r: func(l, r.squeeze(), *args, **kwargs),
                            other._modin_frame,
                        )
                    )
                else:
                    return query_compiler.__constructor__(
                        query_compiler._modin_frame._binary_op(
                            lambda x, y: func(x, y, *args, **kwargs),
                            other._modin_frame,
                        )
                    )
            else:
                if isinstance(other, (list, np.ndarray, pandas.Series)):
                    new_columns = query_compiler.columns
                    new_modin_frame = query_compiler._modin_frame._apply_full_axis(
                        axis,
                        lambda df: func(df, other, *args, **kwargs),
                        new_index=query_compiler.index,
                        new_columns=new_columns,
                    )
                else:
                    new_modin_frame = query_compiler._modin_frame._map(
                        lambda df: func(df, other, *args, **kwargs)
                    )
                return query_compiler.__constructor__(new_modin_frame)