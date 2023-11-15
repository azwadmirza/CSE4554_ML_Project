def mars_serialize_context():
    global _serialize_context
    if _serialize_context is None:
        ctx = pyarrow.default_serialization_context()
        ctx.register_type(SparseNDArray, 'mars.SparseNDArray',
                          custom_serializer=_serialize_sparse_csr_list,
                          custom_deserializer=_deserialize_sparse_csr_list)
        ctx.register_type(DataTuple, 'mars.DataTuple',
                          custom_serializer=_serialize_data_tuple,
                          custom_deserializer=_deserialize_data_tuple)
        _serialize_context = ctx
    return _serialize_context