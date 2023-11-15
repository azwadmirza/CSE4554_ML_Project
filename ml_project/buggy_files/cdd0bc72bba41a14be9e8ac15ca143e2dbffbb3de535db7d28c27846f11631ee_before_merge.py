  def call(self, inputs, memory=None, mask=None, cache=None, training=None):  # pylint: disable=arguments-differ
    """Runs the layer.

    Args:
      inputs: The sequence of queries. A tensor of shape :math:`[B, T_1, ...]`.
      memory: The sequence to attend. A tensor of shape :math:`[B, T_2, ...]`.
        If ``None``, computes self-attention.
      mask: The dot product mask. A boolean tensor of shape :math:`[B, T_2]` or
        :math:`[B, T_1, T_2]`.
      cache: An optional tuple containing projected keys and values from the
        previous step. Tensors of shape :math:`[B, H, T_2, D / H]`.
      training: Run in training mode.

    Returns:
      A tuple with the attention context, the updated cache and the attention
      probabilities of the first head (if :obj:`return_attention` is ``True``).
    """

    def _compute_kv(x):
      keys = self.linear_keys(x)
      keys = split_heads(keys, self.num_heads)
      values = self.linear_values(x)
      values = split_heads(values, self.num_heads)
      return keys, values

    # Compute queries.
    queries = self.linear_queries(inputs)
    queries = split_heads(queries, self.num_heads)
    queries *= self.num_units_per_head**-0.5

    # Compute keys and values.
    if memory is None:
      keys, values = _compute_kv(inputs)
      if cache:
        keys = tf.concat([cache[0], keys], axis=2)
        values = tf.concat([cache[1], values], axis=2)
    else:
      if cache:
        keys, values = tf.cond(
            tf.equal(tf.shape(cache[0])[2], 0),
            true_fn=lambda: _compute_kv(memory),
            false_fn=lambda: cache)
      else:
        keys, values = _compute_kv(memory)

    if self.maximum_relative_position is not None:
      if memory is not None:
        raise ValueError("Relative position representations only supports self-attention")
      keys_length = tf.shape(keys)[2]
      relative_pos = relative_positions(
          keys_length,
          self.maximum_relative_position,
          with_cache=bool(cache))
      relative_repr_keys = tf.gather(self.relative_position_keys, relative_pos)
      relative_repr_values = tf.gather(self.relative_position_values, relative_pos)
    else:
      relative_repr_keys = None
      relative_repr_values = None

    cache = (keys, values)

    # Dot product attention.
    dot = tf.matmul(queries, keys, transpose_b=True)
    if relative_repr_keys is not None:
      dot += matmul_with_relative_representations(queries, relative_repr_keys, transpose_b=True)
    if mask is not None:
      mask = tf.cast(mask, tf.float32)
      if mask.shape.rank == 2:
        mask = tf.expand_dims(mask, 1)  # Broadcast on time dimension.
      mask = tf.expand_dims(mask, 1)  # Broadcast on head dimension.
      dot = tf.cast(tf.cast(dot, tf.float32) * mask + ((1.0 - mask) * tf.float32.min), dot.dtype)
    attn = tf.cast(tf.nn.softmax(tf.cast(dot, tf.float32)), dot.dtype)
    drop_attn = common.dropout(attn, self.dropout, training=training)
    heads = tf.matmul(drop_attn, values)
    if relative_repr_values is not None:
      heads += matmul_with_relative_representations(drop_attn, relative_repr_values)

    # Concatenate all heads output.
    combined = combine_heads(heads)
    outputs = self.linear_output(combined)
    if self.return_attention:
      return outputs, cache, attn
    return outputs, cache