    def tile(cls, op: 'DataFrameToCSV'):
        in_df = op.input
        out_df = op.outputs[0]

        if in_df.ndim == 2:
            # make sure only 1 chunk on the column axis
            in_df = in_df.rechunk({1: in_df.shape[1]})._inplace_tile()

        one_file = op.one_file

        out_chunks = [], []
        for chunk in in_df.chunks:
            chunk_op = op.copy().reset_key()
            if not one_file:
                index_value = parse_index(chunk.index_value.to_pandas()[:0], chunk)
                if chunk.ndim == 2:
                    out_chunk = chunk_op.new_chunk([chunk], shape=(0, 0),
                                                   index_value=index_value,
                                                   columns_value=out_df.columns_value,
                                                   dtypes=out_df.dtypes,
                                                   index=chunk.index)
                else:
                    out_chunk = chunk_op.new_chunk([chunk], shape=(0,),
                                                   index_value=index_value,
                                                   dtype=out_df.dtype,
                                                   index=chunk.index)
                out_chunks[0].append(out_chunk)
            else:
                chunk_op._output_stat = True
                chunk_op._stage = OperandStage.map
                # bytes of csv
                kws = [{
                    'shape': (),
                    'dtype': np.dtype(np.str_),
                    'index': chunk.index,
                    'order': TensorOrder.C_ORDER,
                    'output_type': OutputType.scalar,
                    'type': 'csv',
                }, {
                    'shape': (),
                    'dtype': np.dtype(np.intp),
                    'index': chunk.index,
                    'order': TensorOrder.C_ORDER,
                    'output_type': OutputType.scalar,
                    'type': 'stat',
                }]
                chunks = chunk_op.new_chunks([chunk], kws=kws, output_limit=len(kws))
                out_chunks[0].append(chunks[0])
                out_chunks[1].append(chunks[1])

        if not one_file:
            out_chunks = out_chunks[0]
        else:
            stat_chunk = DataFrameToCSVStat(path=op.path, dtype=np.dtype(np.int64),
                                            storage_options=op.storage_options).new_chunk(
                out_chunks[1], shape=(len(out_chunks[0]),), order=TensorOrder.C_ORDER)
            new_out_chunks = []
            for c in out_chunks[0]:
                op = DataFrameToCSV(stage=OperandStage.agg, path=op.path,
                                    storage_options=op.storage_options,
                                    output_types=op.output_types)
                if out_df.ndim == 2:
                    out_chunk = op.new_chunk(
                        [c, stat_chunk], shape=(0, 0), dtypes=out_df.dtypes,
                        index_value=out_df.index_value,
                        columns_value=out_df.columns_value,
                        index=c.index)
                else:
                    out_chunk = op.new_chunk(
                        [c, stat_chunk], shape=(0,), dtype=out_df.dtype,
                        index_value=out_df.index_value, index=c.index)
                new_out_chunks.append(out_chunk)
            out_chunks = new_out_chunks

        new_op = op.copy()
        params = out_df.params.copy()
        if out_df.ndim == 2:
            params.update(dict(chunks=out_chunks, nsplits=((0,) * in_df.chunk_shape[0], (0,))))
        else:
            params.update(dict(chunks=out_chunks, nsplits=((0,) * in_df.chunk_shape[0],)))
        return new_op.new_tileables([in_df], **params)