    def _pandas_read_csv(cls, f, op):
        csv_kwargs = op.extra_params.copy()
        out_df = op.outputs[0]
        start, end = _find_chunk_start_end(f, op.offset, op.size)
        f.seek(start)
        b = FixedSizeFileObject(f, end - start)
        if hasattr(out_df, 'dtypes'):
            dtypes = out_df.dtypes
        else:
            # Output will be a Series in some optimize rules.
            dtypes = pd.Series([out_df.dtype], index=[out_df.name])
        if end == start:
            # the last chunk may be empty
            df = build_empty_df(dtypes)
            if op.keep_usecols_order and not isinstance(op.usecols, list):
                # convert to Series, if usecols is a scalar
                df = df[op.usecols]
        else:
            if start == 0:
                # The first chunk contains header
                # As we specify names and dtype, we need to skip header rows
                csv_kwargs['skiprows'] = 1 if op.header == 'infer' else op.header
            if op.usecols:
                usecols = op.usecols if isinstance(op.usecols, list) else [op.usecols]
            else:
                usecols = op.usecols
            if contain_arrow_dtype(dtypes):
                # when keep_default_na is True which is default,
                # will replace null value with np.nan,
                # which will cause failure when converting to arrow string array
                csv_kwargs['keep_default_na'] = False
            df = pd.read_csv(b, sep=op.sep, names=op.names, index_col=op.index_col, usecols=usecols,
                             dtype=dtypes.to_dict(), nrows=op.nrows, **csv_kwargs)
            if op.keep_usecols_order:
                df = df[op.usecols]
        return df