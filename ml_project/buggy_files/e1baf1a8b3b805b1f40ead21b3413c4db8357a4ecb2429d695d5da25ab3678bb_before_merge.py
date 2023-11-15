def _normalize_by_window_size(dims, strides, padding):
  def rescale(outputs, inputs):
    one = np.ones(inputs.shape[1:3], dtype=inputs.dtype)
    window_sizes = lax.reduce_window(one, 0., lax.add, dims, strides, padding)
    return outputs / window_sizes
  return rescale