  def __init__(self, layer, quantize_config=None, **kwargs):
    """Create a quantize annotate wrapper over a keras layer.

    Args:
      layer: The keras layer to be quantized.
      quantize_config: `QuantizeConfig` to quantize layer.
      **kwargs: Additional keyword arguments to be passed to the keras layer.
    """
    super(QuantizeAnnotate, self).__init__(layer, **kwargs)

    self.quantize_config = quantize_config

    self._track_trackable(layer, name='layer')
    # Enables end-user to annotate the first layer in Sequential models, while
    # passing the input shape to the original layer.
    #
    # tf.keras.Sequential(
    #   quantize_annotate_layer(tf.keras.layers.Dense(2, input_shape=(3,)))
    # )
    #
    # as opposed to
    #
    # tf.keras.Sequential(
    #   quantize_annotate_layer(tf.keras.layers.Dense(2), input_shape=(3,))
    # )
    #
    # Without this code, the QuantizeAnnotate wrapper doesn't have an input
    # shape and being the first layer, this causes the model to not be
    # built. Being not built is confusing since the end-user has passed an
    # input shape.
    if (not hasattr(self, '_batch_input_shape') and
        hasattr(layer, '_batch_input_shape')):
      self._batch_input_shape = self.layer._batch_input_shape  # pylint: disable=protected-access