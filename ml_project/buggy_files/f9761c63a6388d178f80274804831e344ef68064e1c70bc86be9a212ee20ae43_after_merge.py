    def _cudf_read_csv(cls, op):  # pragma: no cover
        if op.usecols:
            usecols = op.usecols if isinstance(op.usecols, list) else [op.usecols]
        else:
            usecols = op.usecols
        csv_kwargs = op.extra_params
        if op.offset == 0:
            df = cudf.read_csv(op.path, byte_range=(op.offset, op.size), sep=op.sep, usecols=usecols, **csv_kwargs)
        else:
            df = cudf.read_csv(op.path, byte_range=(op.offset, op.size), sep=op.sep, names=op.names,
                               usecols=usecols, nrows=op.nrows, **csv_kwargs)

        if op.keep_usecols_order:
            df = df[op.usecols]
        return df