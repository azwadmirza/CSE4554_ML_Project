    def execute(cls, ctx, op):
        xdf = cudf if op.gpu else pd
        out_df = op.outputs[0]
        csv_kwargs = op.extra_params.copy()

        with open_file(op.path, compression=op.compression, storage_options=op.storage_options) as f:
            if op.compression is not None:
                # As we specify names and dtype, we need to skip header rows
                csv_kwargs['skiprows'] = 1 if op.header == 'infer' else op.header
                dtypes = op.outputs[0].dtypes
                if contain_arrow_dtype(dtypes):
                    # when keep_default_na is True which is default,
                    # will replace null value with np.nan,
                    # which will cause failure when converting to arrow string array
                    csv_kwargs['keep_default_na'] = False
                    csv_kwargs['dtype'] = cls._select_arrow_dtype(dtypes)
                df = xdf.read_csv(f, sep=op.sep, names=op.names, index_col=op.index_col,
                                  usecols=op.usecols, nrows=op.nrows, **csv_kwargs)
                if op.keep_usecols_order:
                    df = df[op.usecols]
            else:
                df = cls._cudf_read_csv(op) if op.gpu else cls._pandas_read_csv(f, op)

        ctx[out_df.key] = df