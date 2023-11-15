    def tile(cls, op):
        tensor = op.tensor
        pk = op.pk
        out = op.outputs[0]
        index_path = op.index_path
        ctx = get_context()
        fs = None
        if index_path is not None:
            fs = get_fs(index_path, op.storage_options)

        # check index_path for distributed
        if getattr(ctx, 'running_mode', None) == RunningMode.distributed:
            if index_path is not None:
                if isinstance(fs, LocalFileSystem):
                    raise ValueError('`index_path` cannot be local file dir '
                                     'for distributed index building')

        if index_path is not None:
            # check if the index path is empty
            try:
                files = [f for f in fs.ls(index_path) if 'proxima_' in f]
                if files:
                    raise ValueError(f'Directory {index_path} contains built proxima index, '
                                     f'clean them to perform new index building')
            except FileNotFoundError:
                # if not exist, create directory
                fs.mkdir(index_path)

        # make sure all inputs have known chunk sizes
        check_chunks_unknown_shape(op.inputs, TilesError)

        nsplit = decide_unify_split(tensor.nsplits[0], pk.nsplits[0])
        if op.topk is not None:
            nsplit = cls._get_atleast_topk_nsplit(nsplit, op.topk)

        if tensor.chunk_shape[1] > 1:
            tensor = tensor.rechunk({0: nsplit, 1: tensor.shape[1]})._inplace_tile()
        else:
            tensor = tensor.rechunk({0: nsplit})._inplace_tile()
        pk = pk.rechunk({0: nsplit})._inplace_tile()

        out_chunks = []
        for chunk, pk_col_chunk in zip(tensor.chunks, pk.chunks):
            chunk_op = op.copy().reset_key()
            chunk_op._stage = OperandStage.map
            out_chunk = chunk_op.new_chunk([chunk, pk_col_chunk],
                                           index=pk_col_chunk.index)
            out_chunks.append(out_chunk)

        logger.warning(f"index chunks count: {len(out_chunks)} ")

        params = out.params
        params['chunks'] = out_chunks
        params['nsplits'] = ((1,) * len(out_chunks),)
        new_op = op.copy()
        return new_op.new_tileables(op.inputs, kws=[params])