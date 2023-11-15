  def __call__(self, encoder_state, decoder_zero_state):  # pylint: disable=arguments-differ
    """Returns the initial decoder state.

    Args:
      encoder_state: The encoder state.
      decoder_zero_state: The default decoder state.

    Returns:
      The decoder initial state.
    """
    inputs = [encoder_state, decoder_zero_state]
    # Always build for backward compatibility.
    self.build(compat.nest.map_structure(lambda x: x.shape, inputs))
    return self.call(inputs)