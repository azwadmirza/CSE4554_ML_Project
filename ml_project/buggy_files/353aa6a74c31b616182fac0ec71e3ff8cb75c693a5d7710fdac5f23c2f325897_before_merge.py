    def execute(cls, ctx, op):
        xdf = cudf if op.gpu else pd
        out_df = op.outputs[0]
        csv_kwargs = op.extra_params.copy()

        with open_file(op.path, compression=op.compression, storage_options=op.storage_options) as f:
            if op.compression is not None:
                # As we specify names and dtype, we need to skip header rows
                csv_kwargs['skiprows'] = 1 if op.header == 'infer' else op.header
                df = xdf.read_csv(BytesIO(f.read()), sep=op.sep, names=op.names, index_col=op.index_col,
                                  dtype=out_df.dtypes.to_dict(), **csv_kwargs)
            else:
                start, end = _find_chunk_start_end(f, op.offset, op.size)
                f.seek(start)
                b = BytesIO(f.read(end - start))
                if end == start:
                    # the last chunk may be empty
                    df = build_empty_df(out_df.dtypes)
                else:
                    if start == 0:
                        # The first chunk contains header
                        # As we specify names and dtype, we need to skip header rows
                        csv_kwargs['skiprows'] = 1 if op.header == 'infer' else op.header
                    df = xdf.read_csv(b, sep=op.sep, names=op.names, index_col=op.index_col,
                                      dtype=out_df.dtypes.to_dict(), **csv_kwargs)
        ctx[out_df.key] = df