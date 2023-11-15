  def _call(self, features, labels, params, mode):
    training = mode == tf.estimator.ModeKeys.TRAIN
    self.examples_inputter.build()

    features_length = self.features_inputter.get_length(features)
    source_inputs = self.features_inputter.make_inputs(features, training=training)
    with tf.variable_scope("encoder"):
      encoder_outputs, encoder_state, encoder_sequence_length = self.encoder.encode(
          source_inputs,
          sequence_length=features_length,
          mode=mode)

    target_vocab_size = self.labels_inputter.vocabulary_size
    target_dtype = self.labels_inputter.dtype
    output_layer = None
    if EmbeddingsSharingLevel.share_target_embeddings(self.share_embeddings):
      output_layer = layers.Dense(
          target_vocab_size,
          weight=self.labels_inputter.embedding,
          transpose=True,
          dtype=target_dtype)
      with tf.name_scope(tf.get_variable_scope().name + "/"):
        output_layer.build([None, self.decoder.output_size])

    if labels is not None:
      target_inputs = self.labels_inputter.make_inputs(labels, training=training)
      with tf.variable_scope("decoder"):
        sampling_probability = None
        if mode == tf.estimator.ModeKeys.TRAIN:
          sampling_probability = get_sampling_probability(
              tf.train.get_or_create_global_step(),
              read_probability=params.get("scheduled_sampling_read_probability"),
              schedule_type=params.get("scheduled_sampling_type"),
              k=params.get("scheduled_sampling_k"))

        logits, _, _, attention = self.decoder.decode(
            target_inputs,
            self.labels_inputter.get_length(labels),
            vocab_size=target_vocab_size,
            initial_state=encoder_state,
            sampling_probability=sampling_probability,
            embedding=self.labels_inputter.embedding,
            output_layer=output_layer,
            mode=mode,
            memory=encoder_outputs,
            memory_sequence_length=encoder_sequence_length,
            return_alignment_history=True)
        if "alignment" in labels:
          outputs = {
              "logits": logits,
              "attention": attention
          }
        else:
          outputs = logits
    else:
      outputs = None

    if mode != tf.estimator.ModeKeys.TRAIN:
      with tf.variable_scope("decoder", reuse=labels is not None):
        batch_size = tf.shape(tf.contrib.framework.nest.flatten(encoder_outputs)[0])[0]
        beam_width = params.get("beam_width", 1)
        maximum_iterations = params.get("maximum_iterations", 250)
        minimum_length = params.get("minimum_decoding_length", 0)
        sample_from = params.get("sampling_topk", 1)
        sample_temperature = params.get("sampling_temperature", 1)
        start_tokens = tf.fill([batch_size], constants.START_OF_SENTENCE_ID)
        end_token = constants.END_OF_SENTENCE_ID

        if beam_width <= 1:
          sampled_ids, _, sampled_length, log_probs, alignment = self.decoder.dynamic_decode(
              self.labels_inputter.embedding,
              start_tokens,
              end_token,
              vocab_size=target_vocab_size,
              initial_state=encoder_state,
              output_layer=output_layer,
              maximum_iterations=maximum_iterations,
              minimum_length=minimum_length,
              mode=mode,
              memory=encoder_outputs,
              memory_sequence_length=encoder_sequence_length,
              dtype=target_dtype,
              return_alignment_history=True,
              sample_from=sample_from,
              sample_temperature=sample_temperature)
        else:
          length_penalty = params.get("length_penalty", 0)
          sampled_ids, _, sampled_length, log_probs, alignment = (
              self.decoder.dynamic_decode_and_search(
                  self.labels_inputter.embedding,
                  start_tokens,
                  end_token,
                  vocab_size=target_vocab_size,
                  initial_state=encoder_state,
                  output_layer=output_layer,
                  beam_width=beam_width,
                  length_penalty=length_penalty,
                  maximum_iterations=maximum_iterations,
                  minimum_length=minimum_length,
                  mode=mode,
                  memory=encoder_outputs,
                  memory_sequence_length=encoder_sequence_length,
                  dtype=target_dtype,
                  return_alignment_history=True,
                  sample_from=sample_from,
                  sample_temperature=sample_temperature))

      target_vocab_rev = self.labels_inputter.vocabulary_lookup_reverse()
      target_tokens = target_vocab_rev.lookup(tf.cast(sampled_ids, tf.int64))

      if params.get("replace_unknown_target", False):
        if alignment is None:
          raise TypeError("replace_unknown_target is not compatible with decoders "
                          "that don't return alignment history")
        if not isinstance(self.features_inputter, inputters.WordEmbedder):
          raise TypeError("replace_unknown_target is only defined when the source "
                          "inputter is a WordEmbedder")
        source_tokens = features["tokens"]
        if beam_width > 1:
          source_tokens = tf.contrib.seq2seq.tile_batch(source_tokens, multiplier=beam_width)
        # Merge batch and beam dimensions.
        original_shape = tf.shape(target_tokens)
        target_tokens = tf.reshape(target_tokens, [-1, original_shape[-1]])
        attention = tf.reshape(alignment, [-1, tf.shape(alignment)[2], tf.shape(alignment)[3]])
        # We don't have attention for </s> but ensure that the attention time dimension matches
        # the tokens time dimension.
        attention = reducer.align_in_time(attention, tf.shape(target_tokens)[1])
        replaced_target_tokens = replace_unknown_target(target_tokens, source_tokens, attention)
        target_tokens = tf.reshape(replaced_target_tokens, original_shape)

      predictions = {
          "tokens": target_tokens,
          "length": sampled_length,
          "log_probs": log_probs
      }
      if alignment is not None:
        predictions["alignment"] = alignment
    else:
      predictions = None

    return outputs, predictions