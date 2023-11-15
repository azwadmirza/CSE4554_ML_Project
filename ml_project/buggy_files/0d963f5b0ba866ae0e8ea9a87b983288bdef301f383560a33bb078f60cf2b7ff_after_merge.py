  def __init__(self, layer, quantize_config, **kwargs):
    """Create a quantize emulate wrapper for a keras layer.

    Args:
      layer: The keras layer to be quantized.
      quantize_config: `QuantizeConfig` to quantize layer.
      **kwargs: Additional keyword arguments to be passed to the keras layer.
    """
    if layer is None:
      raise ValueError('`layer` cannot be None.')

    # Check against keras.Model since it is an instance of keras.layers.Layer.
    if not isinstance(layer, tf.keras.layers.Layer) or isinstance(
        layer, tf.keras.Model):
      raise ValueError(
          '`layer` can only be a `tf.keras.layers.Layer` instance. '
          'You passed an instance of type: {input}.'.format(
              input=layer.__class__.__name__))

    if quantize_config is None:
      raise ValueError('quantize_config cannot be None. It is needed to '
                       'quantize a layer.')

    if 'name' not in kwargs:
      kwargs['name'] = self._make_layer_name(layer)

    super(QuantizeWrapper, self).__init__(layer, **kwargs)
    self.quantize_config = quantize_config

    self._track_trackable(layer, name='layer')