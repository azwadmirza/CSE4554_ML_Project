    def __init__(self, index=None, dtypes=None, from_1d_tensors=None,
                 gpu=None, sparse=None, **kw):
        super().__init__(_index=index, _dtypes=dtypes, _from_1d_tensors=from_1d_tensors,
                         _gpu=gpu, _sparse=sparse, _object_type=ObjectType.dataframe, **kw)