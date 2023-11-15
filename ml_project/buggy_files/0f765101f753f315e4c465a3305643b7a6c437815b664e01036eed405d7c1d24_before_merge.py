def quantize_annotate_model(to_annotate):
  """Annotate a model to be quantized.

  This function does not actually quantize anything. It is merely to specify
  that the model needs to be quantized.

  This function is intended to be used in conjunction with the
  `quantize_annotate_layer`
  API. It's otherwise simpler to use `quantize_model`.

  Annotate a model while overriding the default behavior for one layer:

  ```python
  quantize_config = MyDenseQuantizeConfig()

  model = quantize_annotate_model(keras.Sequential([
      layers.Dense(10, activation='relu', input_shape=(100,)),
      quantize_annotate_layer(layers.Dense(2, activation='sigmoid'),
      quantize_config=quantize_config)
  ])))
  ```

  Note that this function removes the optimizer from the original model.

  Args:
    to_annotate: tf.keras model to annotate to be quantized.

  Returns:
    New tf.keras model with each layer in the model wrapped with
    `QuantizeAnnotate`.
  """
  if to_annotate is None:
    raise ValueError('`to_annotate` cannot be None')

  if not isinstance(to_annotate, keras.Model):
    raise ValueError(
        '`to_annotate` can only be a `tf.keras.Model` instance. Use '
        'the `quantize_annotate_layer` API to handle individual layers. '
        'You passed an instance of type: {input}.'.format(
            input=to_annotate.__class__.__name__))

  def _add_quant_wrapper(layer):
    # Already annotated layer. No need to wrap.
    if isinstance(layer, quantize_annotate_mod.QuantizeAnnotate):
      return layer

    return quantize_annotate_mod.QuantizeAnnotate(layer)

  return keras.models.clone_model(
      to_annotate, input_tensors=None, clone_function=_add_quant_wrapper)