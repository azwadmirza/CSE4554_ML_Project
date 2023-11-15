def _index_to_gather(x_shape, idx):
  # Remove ellipses and add trailing slice(None)s.
  idx = _canonicalize_tuple_index(len(x_shape), idx)

  # Check for advanced indexing:
  # https://docs.scipy.org/doc/numpy/reference/arrays.indexing.html#advanced-indexing

  # Do the advanced indexing axes appear contiguously? If not, NumPy semantics
  # move the advanced axes to the front.
  advanced_axes_are_contiguous = False

  advanced_indexes = None

  # The positions of the advanced indexing axes in `idx`.
  idx_advanced_axes = []

  # The positions of the advanced indexes in x's shape.
  # collapsed, after None axes have been removed. See below.
  x_advanced_axes = None

  if _is_advanced_int_indexer(idx):
    idx_no_nones = [(i, d) for i, d in enumerate(idx) if d is not None]
    advanced_pairs = (
      (asarray(e), i, j) for j, (i, e) in enumerate(idx_no_nones)
      if (isinstance(e, Sequence) or isinstance(e, ndarray)))
    advanced_pairs = ((_normalize_index(e, x_shape[j]), i, j)
                      for e, i, j in advanced_pairs)
    advanced_indexes, idx_advanced_axes, x_advanced_axes = zip(*advanced_pairs)
    advanced_axes_are_contiguous = onp.all(onp.diff(idx_advanced_axes) == 1)

  x_axis = 0  # Current axis in x.
  y_axis = 0  # Current axis in y, before collapsing. See below.
  collapsed_y_axis = 0  # Current axis in y, after collapsing.

  # Scatter dimension numbers.
  offset_dims = []
  collapsed_slice_dims = []
  start_index_map = []

  index_dtype = int64 if _max(x_shape, default=0) >= (1 << 31) else int32
  gather_indices = onp.zeros((0,), dtype=index_dtype)  # use onp to save a compilation

  # We perform three transformations to y before the scatter op, in order:
  # First, y is broadcast to slice_shape. In general `y` only need broadcast to
  # the right shape.
  slice_shape = []

  # Next, y is squeezed to remove newaxis_dims. This removes np.newaxis/`None`
  # indices, which the scatter cannot remove itself.
  newaxis_dims = []

  # Finally, we reverse reversed_y_dims to handle slices with negative strides.
  reversed_y_dims = []

  gather_slice_shape = []

  for idx_pos, i in enumerate(idx):
    # Handle the advanced indices here if:
    # * the advanced indices were not contiguous and we are the start.
    # * we are at the position of the first advanced index.
    if (advanced_indexes is not None and
        (advanced_axes_are_contiguous and idx_pos == idx_advanced_axes[0] or
         not advanced_axes_are_contiguous and idx_pos == 0)):
      advanced_indexes = broadcast_arrays(*advanced_indexes)
      shape = advanced_indexes[0].shape
      ndim = len(shape)
      advanced_indexes = [
        lax.convert_element_type(lax.reshape(a, shape + (1,)), index_dtype)
        for a in advanced_indexes]

      # Broadcast gather_indices from [..., k] to [..., 1, 1, ..., 1, k].
      gather_indices = lax.broadcast_in_dim(
        gather_indices, onp.insert(gather_indices.shape, -1, shape),
        tuple(range(gather_indices.ndim - 1)) + (gather_indices.ndim + ndim - 1,))
      gather_indices = concatenate([gather_indices] + advanced_indexes, -1)
      start_index_map.extend(x_advanced_axes)
      collapsed_slice_dims.extend(x_advanced_axes)
      slice_shape.extend(shape)
      y_axis += ndim
      collapsed_y_axis += ndim

    # Per-index bookkeeping for advanced indexes.
    if idx_pos in idx_advanced_axes:
      x_axis += 1
      gather_slice_shape.append(1)
      continue

    try:
      abstract_i = core.get_aval(i)
    except TypeError:
      abstract_i = None
    # Handle basic int indexes.
    if (isinstance(abstract_i, ConcreteArray) or
        isinstance(abstract_i, ShapedArray)) and _int(abstract_i):
      if x_shape[x_axis] == 0:
        # XLA gives error when indexing into an axis of size 0
        raise IndexError(f"index is out of bounds for axis {x_axis} with size 0")
      i = _normalize_index(i, x_shape[x_axis])
      i = lax.convert_element_type(i, index_dtype)
      i = broadcast_to(i, tuple(gather_indices.shape[:-1]) + (1,))
      gather_indices = concatenate((gather_indices, i), -1)
      collapsed_slice_dims.append(x_axis)
      gather_slice_shape.append(1)
      start_index_map.append(x_axis)
      x_axis += 1
    # Handle np.newaxis (None)
    elif i is None:
      slice_shape.append(1)
      newaxis_dims.append(y_axis)
      y_axis += 1
    # Handle slice(None)
    elif _is_slice_none(i):
      slice_shape.append(x_shape[x_axis])
      gather_slice_shape.append(x_shape[x_axis])
      offset_dims.append(collapsed_y_axis)
      collapsed_y_axis += 1
      y_axis += 1
      x_axis += 1
    # Handle slice index (only static, otherwise an error is raised)
    elif isinstance(i, slice):
      if not _all(elt is None or type(core.get_aval(elt)) is ConcreteArray
                  for elt in (i.start, i.stop, i.step)):
        msg = ("Array slice indices must have static start/stop/step to be used "
               "with Numpy indexing syntax. Try lax.dynamic_slice/"
               "dynamic_update_slice instead.")
        raise IndexError(msg)
      start, limit, stride, needs_rev = _static_idx(i, x_shape[x_axis])
      if needs_rev:
        reversed_y_dims.append(collapsed_y_axis)
      if stride == 1:
        i = lax.convert_element_type(start, index_dtype)
        i = broadcast_to(i, tuple(gather_indices.shape[:-1]) + (1,))
        gather_indices = concatenate((gather_indices, i), -1)
        slice_shape.append(limit - start)
        gather_slice_shape.append(limit - start)
        offset_dims.append(collapsed_y_axis)
        start_index_map.append(x_axis)
      else:
        i = arange(start, limit, stride, dtype=index_dtype)
        size = i.shape[0]
        slice_shape.append(size)
        gather_slice_shape.append(1)
        gather_indices_shape = tuple(gather_indices.shape[:-1]) + (size,)
        i = lax.broadcast_in_dim(
            i, shape=gather_indices_shape + (1,),
            broadcast_dimensions=(len(gather_indices_shape) - 1,))
        gather_indices = lax.broadcast_in_dim(
            gather_indices,
            shape=gather_indices_shape + (len(start_index_map),),
            broadcast_dimensions=(
              tuple(range(len(gather_indices_shape) - 1)) +
              (len(gather_indices_shape),)))
        gather_indices = concatenate(
          (gather_indices, i), len(gather_indices_shape))
        start_index_map.append(x_axis)
        collapsed_slice_dims.append(x_axis)

      collapsed_y_axis += 1
      y_axis += 1
      x_axis += 1
    else:
      if (abstract_i is not None and
          not (issubdtype(abstract_i.dtype, integer) or issubdtype(abstract_i.dtype, bool_))):
        msg = ("Indexer must have integer or boolean type, got indexer "
               "with type {} at position {}, indexer value {}")
        raise TypeError(msg.format(abstract_i.dtype.name, idx_pos, i))

      msg = "Indexing mode not yet supported. Open a feature request!\n{}"
      raise IndexError(msg.format(idx))

  dnums = lax.GatherDimensionNumbers(
    offset_dims = tuple(offset_dims),
    collapsed_slice_dims = tuple(sorted(collapsed_slice_dims)),
    start_index_map = tuple(start_index_map)
  )
  return _Indexer(
    slice_shape=slice_shape,
    newaxis_dims=tuple(newaxis_dims),
    gather_slice_shape=gather_slice_shape,
    reversed_y_dims=reversed_y_dims,
    dnums=dnums,
    gather_indices=gather_indices)