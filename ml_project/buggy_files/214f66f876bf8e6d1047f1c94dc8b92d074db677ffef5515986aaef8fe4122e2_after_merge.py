  def __call__(self, encoder_state, decoder_zero_state):  # pylint: disable=arguments-differ
    """Returns the initial decoder state.

    Args:
      encoder_state: The encoder state.
      decoder_zero_state: The default decoder state.

    Returns:
      The decoder initial state.
    """
    inputs = [encoder_state, decoder_zero_state]
    if compat.is_tf2():
      return super(Bridge, self).__call__(inputs)
    # Build by default for backward compatibility.
    if not compat.reuse():
      self.build(compat.nest.map_structure(lambda x: x.shape, inputs))
    return self.call(inputs)