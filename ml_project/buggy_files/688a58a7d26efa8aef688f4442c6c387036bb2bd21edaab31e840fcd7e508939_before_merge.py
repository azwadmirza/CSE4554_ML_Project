    def __init__(self, tensors: Dict[str, Tensor], metainfo=dict()):
        """Creates dict given dict of tensors (name -> Tensor key value pairs)"""
        self._tensors = tensors
        self._metainfo = metainfo
        shape = None
        for name, tensor in tensors.items():
            if shape is None or tensor.ndim > len(shape):
                shape = tensor.shape
            self._len = tensor.count