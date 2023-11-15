    def tile(cls, op: 'DataFrameDrop'):
        inp = op.inputs[0]
        out = op.outputs[0]
        if len(op.inputs) > 1:
            index_chunk = op.index.rechunk({0: (op.index.shape[0],)})._inplace_tile().chunks[0]
        else:
            index_chunk = op.index

        col_to_args = OrderedDict()
        chunks = []
        for c in inp.chunks:
            params = c.params.copy()
            if isinstance(inp, DATAFRAME_TYPE):
                new_dtypes, new_col_id = col_to_args.get(c.index[1], (None, None))

                if new_dtypes is None:
                    new_col_id = len(col_to_args)
                    new_dtypes = op._filter_dtypes(c.dtypes, ignore_errors=True)
                    if len(new_dtypes) == 0:
                        continue
                    col_to_args[c.index[1]] = (new_dtypes, new_col_id)

                params.update(dict(dtypes=new_dtypes, index=(c.index[0], new_col_id),
                                   index_value=c.index_value))
                if op.index is not None:
                    params.update(dict(shape=(np.nan, len(new_dtypes)),
                                       index_value=parse_index(None, (c.key, c.index_value.key))))
                else:
                    params['shape'] = (c.shape[0], len(new_dtypes))
            elif op.index is not None:
                params.update(dict(shape=(np.nan,), index_value=parse_index(None, (c.key, c.index_value.key))))

            chunk_inputs = [c]
            if isinstance(index_chunk, Chunk):
                chunk_inputs.append(index_chunk)

            new_op = op.copy().reset_key()
            new_op._index = index_chunk
            chunks.append(new_op.new_chunk(chunk_inputs, **params))

        new_op = op.copy().reset_key()
        params = out.params.copy()
        if op.index is not None:
            nsplits_list = [(np.nan,) * inp.chunk_shape[0]]
        else:
            nsplits_list = [inp.nsplits[0]]
        if isinstance(inp, DATAFRAME_TYPE):
            nsplits_list.append(tuple(len(dt) for dt, _ in col_to_args.values()))
        params.update(dict(chunks=chunks, nsplits=tuple(nsplits_list)))
        return new_op.new_tileables(op.inputs, **params)