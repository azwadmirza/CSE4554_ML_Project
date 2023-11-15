def _scatter_add_transpose_rule(t, operand, scatter_indices, updates,
                                update_jaxpr, update_consts, dimension_numbers,
                                updates_shape):
  assert scatter_indices is not None
  operand_t = update_t = None
  if operand is None:
    operand_t = t

  if updates is None:
    gather_dnums = GatherDimensionNumbers(
      offset_dims=dimension_numbers.update_window_dims,
      collapsed_slice_dims=dimension_numbers.inserted_window_dims,
      start_index_map=dimension_numbers.scatter_dims_to_operand_dims)
    slice_sizes = []
    pos = 0
    for i in xrange(len(t.shape)):
      if i in dimension_numbers.inserted_window_dims:
        slice_sizes.append(1)
      else:
        slice_sizes.append(updates_shape[dimension_numbers.update_window_dims[pos]])
        pos += 1
    update_t = gather(t, scatter_indices, dimension_numbers=gather_dnums,
                      slice_sizes=slice_sizes)
  return [operand_t, None, update_t]