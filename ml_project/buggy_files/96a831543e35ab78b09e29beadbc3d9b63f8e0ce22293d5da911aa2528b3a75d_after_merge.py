    def get_initial_state(self, inputs=None, batch_size=None, dtype=None):
        """Return an initial (zero) state tuple for this `AttentionWrapper`.

        **NOTE** Please see the initializer documentation for details of how
        to call `get_initial_state` if using an `AttentionWrapper` with a
        `BeamSearchDecoder`.

        Args:
          inputs: The inputs that will be fed to this cell.
          batch_size: `0D` integer tensor: the batch size.
          dtype: The internal state data type.

        Returns:
          An `AttentionWrapperState` tuple containing zeroed out tensors and,
          possibly, empty `TensorArray` objects.

        Raises:
          ValueError: (or, possibly at runtime, InvalidArgument), if
            `batch_size` does not match the output size of the encoder passed
            to the wrapper object at initialization time.
        """
        if inputs is not None:
            batch_size = tf.shape(inputs)[0]
            dtype = inputs.dtype
        with tf.name_scope(
            type(self).__name__ + "ZeroState"
        ):  # pylint: disable=bad-continuation
            if self._initial_cell_state is not None:
                cell_state = self._initial_cell_state
            else:
                cell_state = self._cell.get_initial_state(
                    batch_size=batch_size, dtype=dtype
                )
            error_message = (
                "When calling get_initial_state of AttentionWrapper %s: " % self.name
                + "Non-matching batch sizes between the memory "
                "(encoder output) and the requested batch size. Are you using "
                "the BeamSearchDecoder?  If so, make sure your encoder output "
                "has been tiled to beam_width via "
                "tfa.seq2seq.tile_batch, and the batch_size= argument "
                "passed to get_initial_state is batch_size * beam_width."
            )
            with tf.control_dependencies(
                self._batch_size_checks(batch_size, error_message)
            ):  # pylint: disable=bad-continuation
                cell_state = tf.nest.map_structure(
                    lambda s: tf.identity(s, name="checked_cell_state"), cell_state
                )
            initial_alignments = [
                attention_mechanism.initial_alignments(batch_size, dtype)
                for attention_mechanism in self._attention_mechanisms
            ]
            return AttentionWrapperState(
                cell_state=cell_state,
                attention=tf.zeros(
                    [batch_size, self._get_attention_layer_size()], dtype=dtype
                ),
                alignments=self._item_or_tuple(initial_alignments),
                attention_state=self._item_or_tuple(
                    attention_mechanism.initial_state(batch_size, dtype)
                    for attention_mechanism in self._attention_mechanisms
                ),
                alignment_history=self._item_or_tuple(
                    tf.TensorArray(
                        dtype, size=0, dynamic_size=True, element_shape=alignment.shape
                    )
                    if self._alignment_history
                    else ()
                    for alignment in initial_alignments
                ),
            )