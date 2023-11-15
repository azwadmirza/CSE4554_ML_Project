  def __call__(self, inputs, sequence_length=None, position=None):  # pylint: disable=arguments-differ
    """Apply position encoding to inputs.

    Args:
      inputs: The inputs of shape :math:`[B, T, D]`.
      sequence_length: The length of each sequence of shape :math:`[B]`.
        If ``None``, sequences are assumed to have the same length.
      position: If known, the position to encode (1-indexed).

    Returns:
      A ``tf.Tensor`` of shape :math:`[B, T, D]` where :math:`D` depends on the
      :attr:`reducer`.
    """
    if compat.is_tf2():
      return super(PositionEncoder, self).__call__(
          inputs, sequence_length=sequence_length, position=position)
    self._dtype = inputs.dtype
    # Build by default for backward compatibility.
    if not compat.reuse():
      self.build(inputs.shape)
    return self.call(
        inputs, sequence_length=sequence_length, position=position)