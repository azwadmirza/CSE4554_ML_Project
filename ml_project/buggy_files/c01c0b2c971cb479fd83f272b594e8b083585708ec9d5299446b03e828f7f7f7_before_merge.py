  def _call(self, features, labels, params, mode):
    training = mode == tf.estimator.ModeKeys.TRAIN
    outputs, predictions = None, None

    ids, length = features["ids"], features["length"]
    if mode != tf.estimator.ModeKeys.PREDICT:
      # For training and evaluation, forward the full sequence.
      logits, _ = self._decode(ids, length, training=training)
      outputs = dict(logits=logits)
    else:
      assert_fixed_length = tf.debugging.Assert(
          tf.reduce_all(tf.equal(length, tf.reduce_max(length))),
          ["Language model does not support variable length contexts during "
           "generation, consider setting batch_size or bucket_width to 1"])

      # Run decoder one the context, if any.
      with tf.control_dependencies([assert_fixed_length]):
        context_ids, start_ids = tf.split(ids, [tf.shape(ids)[1] - 1, 1], axis=1)
        context_length = length - 1
        batch_size = tf.shape(context_length)[0]
        state = tf.cond(
            tf.equal(tf.reduce_sum(context_length), 0),
            true_fn=lambda: self.decoder.get_initial_state(batch_size=batch_size, dtype=self.dtype),
            false_fn=lambda: self._decode(context_ids, context_length)[1],
            name=self.name + "/")  # Force the name scope.

      # Iteratively decode from the last decoder state.
      sampled_ids, sampled_length, _ = decoder_util.greedy_decode(
          self._decode,
          tf.squeeze(start_ids, 1),
          constants.END_OF_SENTENCE_ID,
          decode_length=params.get("maximum_iterations", 250),
          state=state,
          min_decode_length=params.get("minimum_decoding_length", 0),
          last_step_as_input=True,
          sample_from=params.get("sampling_topk", 1),
          sample_temperature=params.get("sampling_temperature", 1))

      # Build the full prediction.
      full_ids = tf.concat([ids, sampled_ids], 1)
      full_length = length + sampled_length
      vocab_rev = self.examples_inputter.vocabulary_lookup_reverse()
      tokens = vocab_rev.lookup(tf.cast(full_ids, tf.int64))
      predictions = dict(tokens=tokens, length=full_length)

    return outputs, predictions