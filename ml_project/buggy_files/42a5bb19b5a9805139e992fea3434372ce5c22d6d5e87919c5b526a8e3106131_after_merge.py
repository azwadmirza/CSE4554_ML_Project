def convert_to_fetch(entity):
    from ..core import CHUNK_TYPE, TENSOR_TYPE
    from .fetch import TensorFetch

    if isinstance(entity, CHUNK_TYPE):
        new_op = TensorFetch(dtype=entity.dtype, sparse=entity.op.sparse)
        return new_op.new_chunk(None, entity.shape, index=entity.index,
                                _key=entity.key, _id=entity.id)
    elif isinstance(entity, TENSOR_TYPE):
        new_op = TensorFetch(dtype=entity.dtype, sparse=entity.op.sparse)
        return new_op.new_tensor(None, entity.shape, _key=entity.key, _id=entity.id)
    else:
        raise ValueError('Now only support tensor or chunk type.')