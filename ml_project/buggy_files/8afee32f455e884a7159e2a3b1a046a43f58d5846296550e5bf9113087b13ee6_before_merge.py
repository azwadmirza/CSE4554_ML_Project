        def __init__(self, name, device_dense, device_sparse, compression, sparse_as_dense,
                     config):
            if name is None:
                name = "Distributed%s" % self.__class__.__base__.__name__
            self._name = name
            self._device_dense = device_dense
            self._device_sparse = device_sparse
            self._compression = compression
            self._sparse_as_dense = sparse_as_dense
            self._get_gradients_used = False
            super(self.__class__, self).__init__(**config)