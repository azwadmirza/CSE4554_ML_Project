  def decode(self,
             inputs,
             sequence_length,
             vocab_size=None,
             initial_state=None,
             sampling_probability=None,
             embedding=None,
             output_layer=None,
             mode=tf.estimator.ModeKeys.TRAIN,
             memory=None,
             memory_sequence_length=None):
    _ = memory
    _ = memory_sequence_length

    batch_size = tf.shape(inputs)[0]

    if (sampling_probability is not None
        and (tf.contrib.framework.is_tensor(sampling_probability)
             or sampling_probability > 0.0)):
      if embedding is None:
        raise ValueError("embedding argument must be set when using scheduled sampling")

      tf.summary.scalar("sampling_probability", sampling_probability)
      helper = tf.contrib.seq2seq.ScheduledEmbeddingTrainingHelper(
          inputs,
          sequence_length,
          embedding,
          sampling_probability)
    else:
      helper = tf.contrib.seq2seq.TrainingHelper(inputs, sequence_length)

    cell, initial_state = self._build_cell(
        mode,
        batch_size,
        initial_state=initial_state,
        memory=memory,
        memory_sequence_length=memory_sequence_length,
        dtype=inputs.dtype)

    if output_layer is None:
      output_layer = build_output_layer(self.num_units, vocab_size, dtype=inputs.dtype)

    # With TrainingHelper, project all timesteps at once.
    fused_projection = isinstance(helper, tf.contrib.seq2seq.TrainingHelper)

    decoder = tf.contrib.seq2seq.BasicDecoder(
        cell,
        helper,
        initial_state,
        output_layer=output_layer if not fused_projection else None)

    outputs, state, length = tf.contrib.seq2seq.dynamic_decode(decoder)

    if fused_projection and output_layer is not None:
      logits = output_layer(outputs.rnn_output)
    else:
      logits = outputs.rnn_output
    # Make sure outputs have the same time_dim as inputs
    inputs_len = tf.shape(inputs)[1]
    logits = align_in_time(logits, inputs_len)

    return (logits, state, length)