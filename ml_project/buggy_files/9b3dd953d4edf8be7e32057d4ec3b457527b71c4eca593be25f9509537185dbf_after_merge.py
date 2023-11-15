    def _tile_head_tail(cls, op):
        from ..merge import DataFrameConcat

        inp = op.input
        out = op.outputs[0]
        combine_size = options.combine_size

        chunks = inp.chunks

        new_chunks = []
        for c in chunks:
            chunk_op = op.copy().reset_key()
            params = out.params
            params['index'] = c.index
            params['shape'] = c.shape if np.isnan(c.shape[0]) else out.shape
            new_chunks.append(chunk_op.new_chunk([c], kws=[params]))
        chunks = new_chunks

        while len(chunks) > 1:
            new_size = ceildiv(len(chunks), combine_size)
            new_chunks = []
            for i in range(new_size):
                in_chunks = chunks[combine_size * i: combine_size * (i + 1)]
                chunk_index = (i, 0) if in_chunks[0].ndim == 2 else (i,)
                if len(inp.shape) == 1:
                    shape = (sum(c.shape[0] for c in in_chunks),)
                else:
                    shape = (sum(c.shape[0] for c in in_chunks), in_chunks[0].shape[1])
                concat_chunk = DataFrameConcat(
                    axis=0, output_types=in_chunks[0].op.output_types).new_chunk(
                    in_chunks, index=chunk_index, shape=shape)
                chunk_op = op.copy().reset_key()
                params = out.params
                params['index'] = chunk_index
                params['shape'] = in_chunks[0].shape if np.isnan(in_chunks[0].shape[0]) else out.shape
                new_chunks.append(chunk_op.new_chunk([concat_chunk], kws=[params]))
            chunks = new_chunks

        new_op = op.copy()
        params = out.params
        params['nsplits'] = tuple((s,) for s in out.shape)
        params['chunks'] = chunks
        return new_op.new_tileables(op.inputs, kws=[params])