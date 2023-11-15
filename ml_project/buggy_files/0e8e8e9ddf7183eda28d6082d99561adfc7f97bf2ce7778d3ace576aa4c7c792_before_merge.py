    def _tile_chunks(cls, op, in_tensor, faiss_index, n_sample):
        """
        If the distribution on each chunk is the same,
        refer to:
        https://github.com/facebookresearch/faiss/wiki/FAQ#how-can-i-distribute-index-building-on-several-machines

        1. train an IndexIVF* on a representative sample of the data, store it.
        2. for each node, load the trained index, add the local data to it, store the resulting populated index
        3. on a central node, load all the populated indexes and merge them.
        """
        faiss_index_ = faiss.index_factory(in_tensor.shape[1], faiss_index,
                                           op.faiss_metric_type)
        # Training on sample data when two conditions meet
        # 1. the index type requires for training, e.g. Flat does not require
        # 2. distributions of chunks are the same, in not,
        #    train separately on each chunk data
        need_sample_train = not faiss_index_.is_trained and op.same_distribution

        train_chunk = None
        if need_sample_train:
            # sample data to train
            rs = RandomState(op.seed)
            sampled_index = rs.choice(in_tensor.shape[0], size=n_sample,
                                      replace=False, chunk_size=n_sample)
            sample_tensor = recursive_tile(in_tensor[sampled_index])
            assert len(sample_tensor.chunks) == 1
            sample_chunk = sample_tensor.chunks[0]
            train_op = FaissTrainSampledIndex(faiss_index=faiss_index, metric=op.metric,
                                              return_index_type=op.return_index_type)
            train_chunk = train_op.new_chunk([sample_chunk])
        elif op.gpu:  # pragma: no cover
            # if not need train, and on gpu, just merge data together to train
            in_tensor = in_tensor.rechunk(in_tensor.shape)._inplace_tile()

        # build index for each input chunk
        build_index_chunks = []
        for i, chunk in enumerate(in_tensor.chunks):
            build_index_op = op.copy().reset_key()
            build_index_op._stage = OperandStage.map
            build_index_op._faiss_index = faiss_index
            if train_chunk is not None:
                build_index_chunk = build_index_op.new_chunk(
                    [chunk, train_chunk], index=(i,))
            else:
                build_index_chunk = build_index_op.new_chunk([chunk], index=(i,))
            build_index_chunks.append(build_index_chunk)

        out_chunks = []
        if need_sample_train:
            assert op.n_sample is not None
            # merge all indices into one, do only when trained on sample data
            out_chunk_op = op.copy().reset_key()
            out_chunk_op._faiss_index = faiss_index
            out_chunk_op._stage = OperandStage.agg
            out_chunk = out_chunk_op.new_chunk(build_index_chunks, index=(0,))
            out_chunks.append(out_chunk)
        else:
            out_chunks.extend(build_index_chunks)

        new_op = op.copy()
        return new_op.new_tileables(op.inputs, chunks=out_chunks,
                                    nsplits=((len(out_chunks),),))