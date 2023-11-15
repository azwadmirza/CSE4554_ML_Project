def calc_shape(tensor_shape, index):
    shape = []
    in_axis = 0
    out_axis = 0
    fancy_index = None
    fancy_index_shapes = []
    for ind in index:
        if isinstance(ind, TENSOR_TYPE + TENSOR_CHUNK_TYPE + (np.ndarray,)) and ind.dtype == np.bool_:
            # bool
            shape.append(np.nan if not isinstance(ind, np.ndarray) else ind.sum())
            for i, t_size, size in zip(itertools.count(0), ind.shape, tensor_shape[in_axis:ind.ndim + in_axis]):
                if not np.isnan(t_size) and not np.isnan(size) and t_size != size:
                    raise IndexError(
                        'boolean index did not match indexed array along dimension {0}; '
                        'dimension is {1} but corresponding boolean dimension is {2}'.format(
                            in_axis + i, size, t_size)
                    )
            in_axis += ind.ndim
            out_axis += 1
        elif isinstance(ind, TENSOR_TYPE + TENSOR_CHUNK_TYPE + (np.ndarray,)):
            first_fancy_index = False
            if fancy_index is None:
                first_fancy_index = True
                fancy_index = out_axis
            if isinstance(ind, np.ndarray) and np.any(ind >= tensor_shape[in_axis]):
                out_of_range_index = next(i for i in ind.flat if i >= tensor_shape[in_axis])
                raise IndexError('IndexError: index {0} is out of bounds with size {1}'.format(
                    out_of_range_index, tensor_shape[in_axis]))
            fancy_index_shapes.append(ind.shape)
            in_axis += 1
            if first_fancy_index:
                out_axis += ind.ndim
        elif isinstance(ind, slice):
            if np.isnan(tensor_shape[in_axis]):
                shape.append(np.nan)
            else:
                shape.append(calc_sliced_size(tensor_shape[in_axis], ind))
            in_axis += 1
            out_axis += 1
        elif isinstance(ind, Integral):
            size = tensor_shape[in_axis]
            if not np.isnan(size) and ind >= size:
                raise IndexError('index {0} is out of bounds for axis {1} with size {2}'.format(
                    ind, in_axis, size
                ))
            in_axis += 1
        else:
            assert ind is None
            shape.append(1)

    if fancy_index is not None:
        try:
            if any(np.isnan(np.prod(s)) for s in fancy_index_shapes):
                fancy_index_shape = (np.nan,) * len(fancy_index_shapes[0])
            else:
                fancy_index_shape = broadcast_shape(*fancy_index_shapes)
            shape = shape[:fancy_index] + list(fancy_index_shape) + shape[fancy_index:]
        except ValueError:
            raise IndexError(
                'shape mismatch: indexing arrays could not be broadcast together '
                'with shapes {0}'.format(' '.join(str(s) for s in fancy_index_shapes)))

    return shape