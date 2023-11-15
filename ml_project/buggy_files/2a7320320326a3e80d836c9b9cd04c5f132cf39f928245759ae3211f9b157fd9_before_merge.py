  def _build(self, features, labels, params, mode, config=None):
    features_length = self._get_features_length(features)
    log_dir = config.model_dir if config is not None else None

    source_input_scope = self._get_input_scope(default_name="encoder")
    target_input_scope = self._get_input_scope(default_name="decoder")

    source_inputs = _maybe_reuse_embedding_fn(
        lambda ids: self.source_inputter.transform_data(ids, mode=mode, log_dir=log_dir),
        scope=source_input_scope)(features)

    with tf.variable_scope("encoder"):
      encoder_outputs, encoder_state, encoder_sequence_length = self.encoder.encode(
          source_inputs,
          sequence_length=features_length,
          mode=mode)

    target_vocab_size = self.target_inputter.vocabulary_size
    target_dtype = self.target_inputter.dtype
    target_embedding_fn = _maybe_reuse_embedding_fn(
        lambda ids: self.target_inputter.transform(ids, mode=mode),
        scope=target_input_scope)

    if labels is not None:
      target_inputs = _maybe_reuse_embedding_fn(
          lambda ids: self.target_inputter.transform_data(ids, mode=mode, log_dir=log_dir),
          scope=target_input_scope)(labels)

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
            self._get_labels_length(labels),
            vocab_size=target_vocab_size,
            initial_state=encoder_state,
            sampling_probability=sampling_probability,
            embedding=target_embedding_fn,
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
        batch_size = tf.shape(encoder_sequence_length)[0]
        beam_width = params.get("beam_width", 1)
        maximum_iterations = params.get("maximum_iterations", 250)
        minimum_length = params.get("minimum_decoding_length", 0)
        start_tokens = tf.fill([batch_size], constants.START_OF_SENTENCE_ID)
        end_token = constants.END_OF_SENTENCE_ID

        if beam_width <= 1:
          sampled_ids, _, sampled_length, log_probs, alignment = self.decoder.dynamic_decode(
              target_embedding_fn,
              start_tokens,
              end_token,
              vocab_size=target_vocab_size,
              initial_state=encoder_state,
              maximum_iterations=maximum_iterations,
              minimum_length=minimum_length,
              mode=mode,
              memory=encoder_outputs,
              memory_sequence_length=encoder_sequence_length,
              dtype=target_dtype,
              return_alignment_history=True)
        else:
          length_penalty = params.get("length_penalty", 0)
          sampled_ids, _, sampled_length, log_probs, alignment = (
              self.decoder.dynamic_decode_and_search(
                  target_embedding_fn,
                  start_tokens,
                  end_token,
                  vocab_size=target_vocab_size,
                  initial_state=encoder_state,
                  beam_width=beam_width,
                  length_penalty=length_penalty,
                  maximum_iterations=maximum_iterations,
                  minimum_length=minimum_length,
                  mode=mode,
                  memory=encoder_outputs,
                  memory_sequence_length=encoder_sequence_length,
                  dtype=target_dtype,
                  return_alignment_history=True))

      target_vocab_rev = tf.contrib.lookup.index_to_string_table_from_file(
          self.target_inputter.vocabulary_file,
          vocab_size=target_vocab_size - self.target_inputter.num_oov_buckets,
          default_value=constants.UNKNOWN_TOKEN)
      target_tokens = target_vocab_rev.lookup(tf.cast(sampled_ids, tf.int64))

      if params.get("replace_unknown_target", False):
        if alignment is None:
          raise TypeError("replace_unknown_target is not compatible with decoders "
                          "that don't return alignment history")
        if not isinstance(self.source_inputter, inputters.WordEmbedder):
          raise TypeError("replace_unknown_target is only defined when the source "
                          "inputter is a WordEmbedder")
        source_tokens = features["tokens"]
        if beam_width > 1:
          source_tokens = tf.contrib.seq2seq.tile_batch(source_tokens, multiplier=beam_width)
        # Merge batch and beam dimensions.
        original_shape = tf.shape(target_tokens)
        target_tokens = tf.reshape(target_tokens, [-1, original_shape[-1]])
        attention = tf.reshape(alignment, [-1, tf.shape(alignment)[2], tf.shape(alignment)[3]])
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