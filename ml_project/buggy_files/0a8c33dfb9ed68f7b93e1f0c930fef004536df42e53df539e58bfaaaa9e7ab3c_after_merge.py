  def _add_quant_wrapper(layer):
    """Add annotation wrapper."""
    # Already annotated layer. No need to wrap.
    if isinstance(layer, quantize_annotate_mod.QuantizeAnnotate):
      return layer

    if isinstance(layer, tf.keras.Model):
      raise ValueError(
          'Quantizing a tf.keras Model inside another tf.keras Model is not supported.'
      )

    return quantize_annotate_mod.QuantizeAnnotate(layer)