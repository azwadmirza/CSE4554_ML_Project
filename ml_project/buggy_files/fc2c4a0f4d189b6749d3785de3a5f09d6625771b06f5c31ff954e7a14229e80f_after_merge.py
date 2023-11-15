    def tile(cls, op):
        inp = op.input
        out = op.outputs[0]

        if len(inp.chunks) == 1:
            chunk_op = op.copy().reset_key()
            chunk_param = out.params
            chunk_param['index'] = (0,)
            chunk = chunk_op.new_chunk(inp.chunks, kws=[chunk_param])

            new_op = op.copy()
            param = out.params
            param['chunks'] = [chunk]
            param['nsplits'] = ((np.nan,),)
            return new_op.new_seriess(op.inputs, kws=[param])

        inp = Series(inp)

        if op.dropna:
            inp = inp.dropna()

        inp = inp.groupby(inp).count(method=op.method)

        if op.normalize:
            if op.convert_index_to_interval:
                check_chunks_unknown_shape([op.input], TilesError)
                inp = inp.truediv(op.input.shape[0], axis=0)
            else:
                inp = inp.truediv(inp.sum(), axis=0)

        if op.sort:
            inp = inp.sort_values(ascending=op.ascending)

        ret = recursive_tile(inp)

        chunks = []
        for c in ret.chunks:
            chunk_op = DataFrameValueCounts(
                convert_index_to_interval=op.convert_index_to_interval,
                stage=OperandStage.map)
            chunk_params = c.params
            if op.convert_index_to_interval:
                # convert index to IntervalDtype
                chunk_params['index_value'] = parse_index(pd.IntervalIndex([]),
                                                          c, store_data=False)
            chunks.append(chunk_op.new_chunk([c], kws=[chunk_params]))

        new_op = op.copy()
        params = out.params
        params['chunks'] = chunks
        params['nsplits'] = ret.nsplits
        return new_op.new_seriess(out.inputs, kws=[params])