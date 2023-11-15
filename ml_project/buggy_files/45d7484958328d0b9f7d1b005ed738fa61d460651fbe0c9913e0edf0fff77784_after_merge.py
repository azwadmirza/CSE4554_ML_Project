    def _partial_reduction(cls, agg_op_type, tensor, axis, dtype, keepdims, combine_size, kw=None):
        from ..merge.concatenate import TensorConcatenate
        kw = kw or {}
        axes = sorted(combine_size.keys())

        combine_blocks = [cls._combine_split(i, combine_size, tensor.chunk_shape)
                          for i in range(tensor.ndim)]
        combine_blocks_idxes = [range(len(blocks)) for blocks in combine_blocks]

        chunks = []
        for combine_block_idx, combine_block in izip(itertools.product(*combine_blocks_idxes),
                                                     itertools.product(*combine_blocks)):
            chks = [tensor.cix[idx] for idx in itertools.product(*combine_block)]
            if len(chks) > 1:
                op = TensorConcatenate(axis=axes, dtype=chks[0].dtype)
                chk = op.new_chunk(chks, shape=cls._concatenate_shape(tensor, combine_block))
            else:
                chk = chks[0]
            shape = tuple(s if i not in combine_size else 1
                          for i, s in enumerate(chk.shape) if keepdims or i not in combine_size)
            agg_op = agg_op_type(axis=axis, dtype=dtype, keepdims=keepdims, **kw)
            chunk = agg_op.new_chunk([chk], shape=shape,
                                     index=tuple(idx for i, idx in enumerate(combine_block_idx)
                                                 if keepdims or i not in combine_size))
            chunks.append(chunk)

        nsplits = [
            tuple(c.shape[i] for c in chunks if builtins.all(idx == 0 for j, idx in enumerate(c.index) if j != i))
            for i in range(len(chunks[0].shape))]
        shape = tuple(builtins.sum(nsplit) for nsplit in nsplits)
        agg_op = agg_op_type(axis=axis, dtype=dtype, keepdims=keepdims, combine_size=combine_size, **kw)
        return agg_op.new_tensors([tensor], shape, chunks=chunks, nsplits=nsplits)