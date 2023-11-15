def _gather_shape_rule(operand, start_indices, *, dimension_numbers,
                       slice_sizes):
  """Validates the well-formedness of the arguments to Gather.

  The code implements the checks based on the detailed operation semantics of
  XLA's `Gather <https://www.tensorflow.org/xla/operation_semantics#gather>`_
  operator and following the outline of the implementation of
  ShapeInference::InferGatherShape in TensorFlow.
  """

  offset_dims = dimension_numbers.offset_dims
  collapsed_slice_dims = dimension_numbers.collapsed_slice_dims
  start_index_map = dimension_numbers.start_index_map

  # Note: in JAX, index_vector_dim is always computed as below, cf. the
  # documentation of the GatherDimensionNumbers class.
  index_vector_dim = _rank(start_indices) - 1

  # This case should never happen in JAX, due to the implicit construction of
  # index_vector_dim, but is included for completeness.
  if _rank(start_indices) < index_vector_dim or index_vector_dim < 0:
    raise TypeError(f"Gather index leaf dimension must be within [0, rank("
                    f"start_indices) + 1). rank(start_indices) is "
                    f"{_rank(start_indices)} and gather index leaf dimension "
                    f"is {index_vector_dim}.")

  expanded_start_indices_shape = list(start_indices.shape)

  # This case should never happen in JAX, due to the implicit construction of
  # index_vector_dim, but is included for completeness.
  if len(expanded_start_indices_shape) == index_vector_dim:
    expanded_start_indices_shape.append(1)

  # Start ValidateGatherDimensions
  # In the error messages output by XLA, "offset_dims" is called "Output window
  # dimensions" in error messages. For consistency's sake, our error messages
  # stick to "offset_dims".
  _is_sorted(offset_dims, "gather", "offset_dims")
  _no_duplicate_dims(offset_dims, "gather", "offset_dims")

  output_offset_dim_count = len(offset_dims)
  output_shape_rank = len(offset_dims) + _rank(start_indices) - 1

  for i in range(output_offset_dim_count):
    offset_dim = offset_dims[i]
    if offset_dim < 0 or offset_dim >= output_shape_rank:
      raise TypeError(f"Offset dimension {i} in gather op is out of bounds; "
                      f"got {offset_dim}, but should have been in "
                      f"[0, {output_shape_rank})")

  if len(start_index_map) != start_indices.shape[index_vector_dim]:
    raise TypeError(f"Gather op has {len(start_index_map)} elements in "
                    f"start_index_map and the bound of dimension "
                    f"index_vector_dim={index_vector_dim} of start_indices is "
                    f"{start_indices.shape[index_vector_dim]}. These two "
                    f"numbers must be equal.")

  for i in range(len(start_index_map)):
    operand_dim_for_start_index_i = start_index_map[i]
    if (operand_dim_for_start_index_i < 0 or
        operand_dim_for_start_index_i >= _rank(operand)):
      raise TypeError(f"Invalid start_index_map; domain is "
                      f"[0, {_rank(operand)}), got: "
                      f"{i}->{operand_dim_for_start_index_i}.")

  _no_duplicate_dims(start_index_map, "gather", "start_index_map")

  # _is_sorted and _sorted_dims_in_range are checked in the opposite order
  # compared to the XLA implementation. In cases when the input is not sorted
  # AND there are problematic collapsed_slice_dims, the error message will thus
  # be different.
  _is_sorted(collapsed_slice_dims, "gather", "collapsed_slice_dims")
  _sorted_dims_in_range(collapsed_slice_dims, _rank(operand), "gather",
                        "collapsed_slice_dims")
  _no_duplicate_dims(collapsed_slice_dims, "gather", "collapsed_slice_dims")
  # End ValidateGatherDimensions

  if _rank(operand) != len(slice_sizes):
    raise TypeError(f"Gather op must have one slice size for every input "
                    f"dimension; got: len(slice_sizes)={len(slice_sizes)}, "
                    f"input_shape.rank={_rank(operand)}")

  if len(slice_sizes) != len(offset_dims) + len(collapsed_slice_dims):
    raise TypeError(f"All components of the offset index in a gather op must "
                    f"either be a offset dimension or explicitly collapsed; "
                    f"got len(slice_sizes)={len(slice_sizes)}, "
                    f"output_slice_sizes={offset_dims}, collapsed_slice_dims="
                    f"{collapsed_slice_dims}.")

  for i in range(len(slice_sizes)):
    slice_size = slice_sizes[i]
    corresponding_input_size = operand.shape[i]

    if slice_size < 0 or slice_size > corresponding_input_size:
      raise TypeError(f"Slice size at index {i} in gather op is out of range, "
                      f"must be within [0, {corresponding_input_size + 1}), "
                      f"got {slice_size}.")

  for i in range(len(collapsed_slice_dims)):
    bound = slice_sizes[collapsed_slice_dims[i]]
    if bound > 1:
      raise TypeError(f"Gather op can only collapse slice dims with bound 1 "
                      f"or 0, but bound is {bound} for index "
                      f"{collapsed_slice_dims[i]} at position {i}.")

  expanded_start_indices_shape.pop(index_vector_dim)
  start_indices_shape = iter(expanded_start_indices_shape)

  slice_sizes = iter(np.delete(slice_sizes, collapsed_slice_dims))
  return tuple(next(slice_sizes) if i in offset_dims
               else next(start_indices_shape) for i in range(output_shape_rank))