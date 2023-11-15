  def __init__(self, layer, quantize_config, **kwargs):
    """Create a quantize emulate wrapper for a keras layer.

    Args:
      layer: The keras layer to be quantized.
      quantize_config: `QuantizeConfig` to quantize layer.
      **kwargs: Additional keyword arguments to be passed to the keras layer.
    """

    if quantize_config is None:
      raise ValueError('quantize_config cannot be None. It is needed to '
                       'quantize a layer.')

    if 'name' not in kwargs:
      kwargs['name'] = self._make_layer_name(layer)

    super(QuantizeWrapper, self).__init__(layer, **kwargs)
    self.quantize_config = quantize_config

    self._track_trackable(layer, name='layer')