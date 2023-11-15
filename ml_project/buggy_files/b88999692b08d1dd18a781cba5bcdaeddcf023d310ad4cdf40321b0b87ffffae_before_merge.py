def _scatter_shape_rule(operand, scatter_indices, updates, *, update_jaxpr,
                        update_consts, dimension_numbers, indices_are_sorted,
                        unique_indices):
  """Validates the well-formedness of the ``dimension_numbers`` argument to
  Scatter.

  The code implements the checks based on the detailed operation semantics of
  XLA's `Scatter <https://www.tensorflow.org/xla/operation_semantics#scatter>`_
  operator and following the outline of the implementation of
  ShapeInference::InferScatterShape in TensorFlow.
  """
  rank = lambda arr: len(arr.shape)

  def _is_sorted(dims, name):
    for i in range(1, len(dims)):
      if dims[i] < dims[i - 1]:
        raise TypeError(f"{name} in scatter op must be sorted; got {dims}")

  def _sorted_dims_in_range(dims, rank, name):
    if len(dims) == 0:
      return
    invalid_dim = None
    if dims[0] < 0:
      invalid_dim = dims[0]
    elif dims[-1] >= rank:
      invalid_dim = dims[-1]
    if invalid_dim:
      raise TypeError(f"Invalid {name} set in scatter op; valid range is "
                      f"[0, {rank}); got: {invalid_dim}.")

  def _no_duplicate_dims(dims, name):
    if len(set(dims)) != len(dims):
      raise TypeError(f"{name} in scatter op must not repeat; got: {dims}.")

  update_window_dims = dimension_numbers.update_window_dims
  inserted_window_dims = dimension_numbers.inserted_window_dims
  scatter_dims_to_operand_dims = dimension_numbers.scatter_dims_to_operand_dims
  # Note: in JAX, index_vector_dim is always computed as below, cf. the
  # documentation of the ScatterDimensionNumbers class.
  index_vector_dim = rank(scatter_indices) - 1

  # This case should never happen in JAX, due to the implicit construction of
  # index_vector_dim, but is included for completeness.
  if rank(scatter_indices) < index_vector_dim or index_vector_dim < 0:
    raise TypeError(f"Scatter index leaf dimension must be within [0, "
                    f"rank(scatter_indices) + 1). rank(scatter_indices) is "
                    f"{rank(scatter_indices)} and scatter index leaf "
                    f"dimension is {index_vector_dim}.")

  expanded_scatter_indices_shape = list(scatter_indices.shape)
  # This case should never happen in JAX, due to the implicit construction of
  # index_vector_dim, but is included for completeness.
  if len(expanded_scatter_indices_shape) == index_vector_dim:
    expanded_scatter_indices_shape.append(1)

  expected_updates_rank = (len(expanded_scatter_indices_shape) - 1 +
                           len(update_window_dims))

  if rank(updates) != expected_updates_rank:
    raise TypeError(f"Updates tensor must be of rank {expected_updates_rank}; "
                    f"got {rank(updates)}.")

  # Validate update_window_dims
  _is_sorted(update_window_dims, "update_window_dims")
  _no_duplicate_dims(update_window_dims, "update_window_dims")
  _sorted_dims_in_range(update_window_dims, rank(updates), "update_window_dims")

  # Validate inserted_window_dims
  _is_sorted(inserted_window_dims, "inserted_window_dims")
  _no_duplicate_dims(inserted_window_dims, "inserted_window_dims")
  _sorted_dims_in_range(inserted_window_dims, rank(operand),
                        "inserted_window_dims")

  # Validate window_size
  window_size = len(update_window_dims) + len(inserted_window_dims)
  if rank(operand) != window_size:
    raise TypeError(f"Scatter op has window of size {window_size}; doesn't "
                    f"match operand of rank {rank(operand)}.")

  # Validate scatter_dims_to_operand_dims
  if (len(scatter_dims_to_operand_dims) !=
      scatter_indices.shape[index_vector_dim]):
    raise TypeError(f"Scatter op has {len(scatter_dims_to_operand_dims)} "
                    f"elements in scatter_dims_to_operand_dims and the bound "
                    f"of dimension index_vector_dim={index_vector_dim} of "
                    f"scatter_indices is "
                    f"{scatter_indices.shape[index_vector_dim]}. These two "
                    f"numbers must be equal")

  for i in range(len(scatter_dims_to_operand_dims)):
    dim = scatter_dims_to_operand_dims[i]
    if dim < 0 or dim >= rank(operand):
      raise TypeError(f"Invalid scatter_dims_to_operand_dims mapping; domain "
                      f"is [0, {rank(operand)}), got: {i}->{dim}.")

  _no_duplicate_dims(scatter_dims_to_operand_dims,
                     "scatter_dims_to_operand_dims")

  max_update_slice_sizes = [operand.shape[i] for i in range(len(operand.shape))
                            if not i in set(inserted_window_dims)]

  for i in range(len(update_window_dims)):
    update_window_dim = update_window_dims[i]
    if updates.shape[update_window_dim] > max_update_slice_sizes[i]:
      raise TypeError(f"Bounds of the window dimensions of updates must not "
                      f"exceed the bounds of the corresponding dimensions of "
                      f"operand. For dimension {update_window_dim}, updates "
                      f"bound is {updates.shape[update_window_dim]}, operand "
                      f"bound is {max_update_slice_sizes[i]}.")

  update_scatter_dims = [dim for dim in range(rank(updates)) if dim not in
                         set(update_window_dims)]

  scatter_dims_seen = 0
  for i in update_scatter_dims:
    if scatter_dims_seen == index_vector_dim:
      scatter_dims_seen += 1
    if updates.shape[i] != expanded_scatter_indices_shape[scatter_dims_seen]:
      raise TypeError(f"Bounds of the scatter dimensions of updates must be "
                      f"the same as the bounds of the corresponding dimensions "
                      f"of scatter indices. For scatter dimension {i}, updates "
                      f"bound is {updates.shape[i]}, scatter_indices bound is "
                      f"{expanded_scatter_indices_shape[scatter_dims_seen]}.")
    scatter_dims_seen += 1

  return operand.shape