def _threefry2x32_gpu_translation_rule(c, k1, k2, x1, x2):
  shape = lax.broadcast_shapes(
      c.get_shape(k1).dimensions(), c.get_shape(k2).dimensions(),
      c.get_shape(x1).dimensions(), c.get_shape(x2).dimensions())
  rank = len(shape)
  if 0 in shape:
    zeros = xla_client.ops.Broadcast(
        xla_bridge.constant(c, np.array(0, np.uint32)), shape)
    return xla_client.ops.Tuple(c, [zeros, zeros])
  def _broadcast(x):
    ndims = c.get_shape(x).rank()
    return xla_client.ops.BroadcastInDim(x, shape,
                                         tuple(range(rank - ndims, rank)))
  return cuda_prng.threefry2x32(
      c, (_broadcast(k1), _broadcast(k2)), (_broadcast(x1), _broadcast(x2)))