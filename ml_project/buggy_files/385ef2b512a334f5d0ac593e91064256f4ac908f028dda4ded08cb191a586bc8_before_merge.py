def _gather_shape_rule(operand, start_indices, *, dimension_numbers,
                       slice_sizes):
  if len(operand.shape) != len(slice_sizes):
    msg = ("slice_sizes must have rank equal to the gather operand; "
          "operand.shape={}, slice_sizes={}".format(operand.shape, slice_sizes))
    raise ValueError(msg)
  result_rank = len(dimension_numbers.offset_dims) + start_indices.ndim - 1
  start_indices_shape = iter(start_indices.shape[:-1])
  slice_sizes = iter(np.delete(slice_sizes, dimension_numbers.collapsed_slice_dims))
  return tuple(next(slice_sizes) if i in dimension_numbers.offset_dims
               else next(start_indices_shape) for i in range(result_rank))