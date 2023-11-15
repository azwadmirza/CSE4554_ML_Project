  def transform(self, inputs, mode):
    try:
      embeddings = tf.get_variable("w_embs", dtype=self.dtype, trainable=self.trainable)
    except ValueError:
      # Variable does not exist yet.
      if self.embedding_file:
        pretrained = load_pretrained_embeddings(
            self.embedding_file,
            self.vocabulary_file,
            num_oov_buckets=self.num_oov_buckets,
            with_header=self.embedding_file_with_header,
            case_insensitive_embeddings=self.case_insensitive_embeddings)
        self.embedding_size = pretrained.shape[-1]

        shape = None
        initializer = tf.constant(pretrained.astype(self.dtype.as_numpy_dtype()))
      else:
        shape = [self.vocabulary_size, self.embedding_size]
        initializer = None

      embeddings = tf.get_variable(
          "w_embs",
          shape=shape,
          dtype=self.dtype,
          initializer=initializer,
          trainable=self.trainable)

    outputs = embedding_lookup(embeddings, inputs)

    outputs = tf.layers.dropout(
        outputs,
        rate=self.dropout,
        training=mode == tf.estimator.ModeKeys.TRAIN)

    return outputs