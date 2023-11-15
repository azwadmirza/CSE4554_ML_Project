  def encode(self, inputs, sequence_length=None, mode=tf.estimator.ModeKeys.TRAIN):
    encoder_state = []

    for layer_index, layer in enumerate(self.layers):
      input_depth = inputs.get_shape().as_list()[-1]

      if layer_index == 0:
        # For the first input, make the number of timesteps a multiple of the
        # total reduction factor.
        total_reduction_factor = pow(self.reduction_factor, len(self.layers) - 1)

        current_length = tf.shape(inputs)[1]
        factor = tf.divide(tf.cast(current_length, tf.float32), total_reduction_factor)
        new_length = tf.cast(tf.ceil(factor), tf.int32) * total_reduction_factor
        inputs = pad_in_time(inputs, new_length - current_length)

        # Lengths should not be smaller than the total reduction factor.
        sequence_length = tf.maximum(sequence_length, total_reduction_factor)
      else:
        # In other cases, reduce the time dimension.
        inputs = tf.reshape(
            inputs,
            [tf.shape(inputs)[0], -1, input_depth * self.reduction_factor])
        if sequence_length is not None:
          sequence_length = tf.div(sequence_length, self.reduction_factor)

      with tf.variable_scope("layer_{}".format(layer_index)):
        outputs, state, sequence_length = layer.encode(
            inputs,
            sequence_length=sequence_length,
            mode=mode)

      encoder_state.append(state)
      inputs = outputs

    return (
        outputs,
        self.state_reducer.reduce(encoder_state),
        sequence_length)