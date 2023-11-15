def _gen_dataframe_chunks(splits, out_shape, left_or_right, df):
    out_chunks = []
    if splits.all_axes_can_split():
        # no shuffle for all axes
        kw = {
            'index_shuffle_size':  -1 if splits[0].isdummy() else None,
            'column_shuffle_size': -1 if splits[1].isdummy() else None,
        }
        for out_idx in itertools.product(*(range(s) for s in out_shape)):
            row_idx = splits.get_axis_idx(0, left_or_right, out_idx[0])
            col_idx = splits.get_axis_idx(1, left_or_right, out_idx[1])
            index_min_max = splits.get_axis_split(0, left_or_right, out_idx[0])
            column_min_max = splits.get_axis_split(1, left_or_right, out_idx[1])
            chunk = df.cix[row_idx, col_idx]
            if _need_align_map(chunk, index_min_max, column_min_max,
                               splits[0].isdummy(), splits[1].isdummy()):
                if splits[1].isdummy():
                    dtypes = chunk.dtypes
                else:
                    dtypes = filter_dtypes(chunk.dtypes, column_min_max)
                chunk_kw = {
                    'index_value': chunk.index_value if splits[0].isdummy() else None,
                    'columns_value': chunk.columns if splits[1].isdummy() else None,
                }
                align_op = DataFrameIndexAlignMap(
                    index_min_max=index_min_max, column_min_max=column_min_max,
                    dtypes=dtypes, sparse=chunk.issparse(),
                    object_type=ObjectType.dataframe, **kw)
                out_chunk = align_op.new_chunk([chunk], shape=(np.nan, np.nan), index=out_idx, **chunk_kw)
            else:
                out_chunk = chunk
            out_chunks.append(out_chunk)
    elif splits.one_axis_can_split():
        # one axis needs shuffle
        shuffle_axis = 0 if splits[0] is None else 1
        align_axis = 1 - shuffle_axis

        for align_axis_idx in range(out_shape[align_axis]):
            if align_axis == 0:
                kw = {
                    'index_min_max': splits.get_axis_split(align_axis, left_or_right, align_axis_idx),
                    'index_shuffle_size':  -1 if splits[0].isdummy() else None,
                    'column_shuffle_size': out_shape[shuffle_axis],
                }
                input_idx = splits.get_axis_idx(align_axis, left_or_right, align_axis_idx)
            else:
                kw = {
                    'column_min_max': splits.get_axis_split(align_axis, left_or_right, align_axis_idx),
                    'index_shuffle_size': out_shape[shuffle_axis],
                    'column_shuffle_size': -1 if splits[1].isdummy() else None,
                }
                input_idx = splits.get_axis_idx(align_axis, left_or_right, align_axis_idx)
            input_chunks = [c for c in df.chunks if c.index[align_axis] == input_idx]
            map_chunks = []
            for j, input_chunk in enumerate(input_chunks):
                chunk_kw = dict()
                if align_axis == 0:
                    chunk_kw['index_value'] = input_chunk.index_value if splits[0].isdummy() else None
                else:
                    chunk_kw['columns_value'] = input_chunk.columns if splits[1].isdummy() else None
                map_op = DataFrameIndexAlignMap(sparse=input_chunk.issparse(),
                                                object_type=ObjectType.dataframe, **kw)
                idx = [None, None]
                idx[align_axis] = align_axis_idx
                idx[shuffle_axis] = j
                map_chunks.append(map_op.new_chunk([input_chunk], shape=(np.nan, np.nan), index=tuple(idx), **chunk_kw))
            proxy_chunk = DataFrameShuffleProxy(
                sparse=df.issparse(), object_type=ObjectType.dataframe).new_chunk(map_chunks, shape=())
            for j in range(out_shape[shuffle_axis]):
                chunk_kw = dict()
                if align_axis == 0:
                    chunk_kw['index_value'] = proxy_chunk.inputs[0].inputs[0].index_value if splits[0].isdummy() else None
                else:
                    chunk_kw['columns_value'] = proxy_chunk.inputs[0].inputs[0].columns if splits[1].isdummy() else None
                reduce_idx = (align_axis_idx, j) if align_axis == 0 else (j, align_axis_idx)
                reduce_op = DataFrameIndexAlignReduce(i=j, sparse=proxy_chunk.issparse(),
                                                      shuffle_key=','.join(str(idx) for idx in reduce_idx),
                                                      object_type=ObjectType.dataframe)
                out_chunks.append(
                    reduce_op.new_chunk([proxy_chunk], shape=(np.nan, np.nan), index=reduce_idx, **chunk_kw))
        out_chunks.sort(key=lambda c: c.index)
    else:
        # all axes need shuffle
        assert splits.no_axis_can_split()

        # gen map chunks
        map_chunks = []
        for chunk in df.chunks:
            map_op = DataFrameIndexAlignMap(
                sparse=chunk.issparse(), index_shuffle_size=out_shape[0],
                column_shuffle_size=out_shape[1], object_type=ObjectType.dataframe)
            map_chunks.append(map_op.new_chunk([chunk], shape=(np.nan, np.nan), index=chunk.index))

        proxy_chunk = DataFrameShuffleProxy(object_type=ObjectType.dataframe).new_chunk(
            map_chunks, shape=())

        # gen reduce chunks
        for out_idx in itertools.product(*(range(s) for s in out_shape)):
            reduce_op = DataFrameIndexAlignReduce(i=out_idx,
                                                  sparse=proxy_chunk.issparse(),
                                                  shuffle_key=','.join(str(idx) for idx in out_idx),
                                                  object_type=ObjectType.dataframe)
            out_chunks.append(
                reduce_op.new_chunk([proxy_chunk], shape=(np.nan, np.nan), index=out_idx))

    return out_chunks