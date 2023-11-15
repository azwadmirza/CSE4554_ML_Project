def dynamic_slice_in_dim(operand, start_index, slice_size, axis=0):
  """Convenience wrapper around dynamic_slice applying to one dimension."""
  start_indices = [onp.array([0], dtype=_dtype(start_index))] * operand.ndim
  slice_sizes = list(operand.shape)

  axis = int(axis)
  axis_size = _const(start_index, operand.shape[axis])
  start_indices[axis] = reshape(rem(start_index, axis_size), [1])
  slice_sizes[axis] = int(slice_size)

  start_indices = concatenate(start_indices, 0)
  return dynamic_slice(operand, start_indices, slice_sizes)