def quantize_model(to_quantize):
  """Quantize a whole tf.keras model with the default quantization implementation.

  To be more precise, `quantize_model` creates a model that emulates
  quantization during training and stores information that downstream
  tools will use to produce actually quantized models.

  Quantize a model:

  ```python
  model = quantize_model(
      keras.Sequential([
          layers.Dense(10, activation='relu', input_shape=(100,)),
          layers.Dense(2, activation='sigmoid')
      ]))
  ```

  Note that this function removes the optimizer from the original model.
  Additionally, training the model returned by `quantize_model` will not affect
  the weights of the original model.

  Args:
    to_quantize: tf.keras model to be quantized. It can have pre-trained
      weights.

  Returns:
    Returns a new tf.keras model prepared for quantization.
  """
  if to_quantize is None:
    raise ValueError('`to_quantize` cannot be None')

  if not isinstance(to_quantize, keras.Model):
    raise ValueError(
        '`to_quantize` can only be a `tf.keras.Model` instance. Use '
        'the `quantize_annotate_layer` API to handle individual layers.'
        'You passed an instance of type: {input}.'.format(
            input=to_quantize.__class__.__name__))

  annotated_model = quantize_annotate_model(to_quantize)
  return quantize_apply(annotated_model)