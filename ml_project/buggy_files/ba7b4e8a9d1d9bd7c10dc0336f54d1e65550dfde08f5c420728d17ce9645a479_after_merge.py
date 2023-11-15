def _reduce_prod_jvp_rule(primals, tangents, *, axes):
  operand, = primals
  tangent, = tangents
  input_shape = onp.array(operand.shape)

  n = onp.prod(input_shape[list(axes)])
  non_axes = onp.delete(onp.arange(len(input_shape)), axes)

  # Move the reduced axes to the front, and flatten them to 1D.
  permutation = axes + tuple(non_axes)
  new_shape = (n,) + tuple(input_shape[non_axes])
  operand = reshape(operand, new_shape, permutation)
  tangent = reshape(tangent, new_shape, permutation)

  def _reduce_prod_tree(x, axis=0):
    """Reduce by repeatedly splitting the array and multiplying."""
    while x.shape[axis] > 1:
      n = x.shape[axis]
      n1 = (n + 1) // 2
      n2 = n - n1
      x1 = slice_in_dim(x, 0, n1)
      x2 = slice_in_dim(x, n1, None)
      if n2 != n1:
        paddings = [(0, 0, 0)] * len(x.shape)
        paddings[axis] = (0, 1, 0)
        x2 = pad(x2, _const(x, 1), paddings)
      x = x1 * x2
    if x.shape[axis] == 0:
      return full(input_shape[non_axes], _one(x))
    return squeeze(x, (axis,))

  return api.jvp(_reduce_prod_tree, (operand,), (tangent,))