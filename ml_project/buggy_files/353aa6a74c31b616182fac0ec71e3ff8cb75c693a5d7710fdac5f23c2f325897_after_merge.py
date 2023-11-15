    def execute(cls, ctx, op):
        xdf = cudf if op.gpu else pd
        out_df = op.outputs[0]
        csv_kwargs = op.extra_params.copy()

        with open_file(op.path, compression=op.compression, storage_options=op.storage_options) as f:
            if op.compression is not None:
                # As we specify names and dtype, we need to skip header rows
                csv_kwargs['skiprows'] = 1 if op.header == 'infer' else op.header
                df = xdf.read_csv(BytesIO(f.read()), sep=op.sep, names=op.names, index_col=op.index_col,
                                  dtype=cls._validate_dtypes(op.outputs[0].dtypes, op.gpu), **csv_kwargs)
            else:
                df = cls._cudf_read_csv(op) if op.gpu else cls._pandas_read_csv(f, op)

        ctx[out_df.key] = df