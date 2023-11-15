    def __init__(self, input_=None, index=None, dtype=None,
                 gpu=None, sparse=None, **kw):
        super().__init__(_input=input_, _index=index, _dtype=dtype, _gpu=gpu,
                         _sparse=sparse, _output_types=[OutputType.series], **kw)