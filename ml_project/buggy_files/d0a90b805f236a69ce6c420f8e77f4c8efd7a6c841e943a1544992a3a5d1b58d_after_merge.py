    def __init__(self, data=None, dtype=None, copy=False, name=None, tupleize_cols=True,
                 chunk_size=None, gpu=None, sparse=None, names=None, num_partitions=None):
        # make sure __getattr__ does not result in stack overflow
        self._data = None

        need_repart = False
        if isinstance(data, INDEX_TYPE):
            if not hasattr(data, 'data'):
                # IndexData
                index = _Index(data)
            else:
                index = data
            need_repart = num_partitions is not None
        else:
            if isinstance(data, (Base, Entity)):
                name = name if name is not None else getattr(data, 'name', None)
                index = from_tileable_index(data, dtype=dtype, name=name, names=names)
                need_repart = num_partitions is not None
            else:
                if not isinstance(data, pd.Index):
                    name = name if name is not None else getattr(data, 'name', None)
                    pd_index = pd.Index(data=data, dtype=dtype, copy=copy, name=name,
                                        tupleize_cols=tupleize_cols)
                else:
                    pd_index = data

                if num_partitions is not None:
                    chunk_size = ceildiv(len(pd_index), num_partitions)
                index = from_pandas_index(pd_index, chunk_size=chunk_size,
                                          gpu=gpu, sparse=sparse)

        if need_repart:
            index = index.rebalance(num_partitions=num_partitions)
        super().__init__(index.data)