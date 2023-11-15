    def call(self, inputs, state, **kwargs):
        """Perform a step of attention-wrapped RNN.

        - Step 1: Mix the `inputs` and previous step's `attention` output via
          `cell_input_fn`.
        - Step 2: Call the wrapped `cell` with this input and its previous
          state.
        - Step 3: Score the cell's output with `attention_mechanism`.
        - Step 4: Calculate the alignments by passing the score through the
          `normalizer`.
        - Step 5: Calculate the context vector as the inner product between the
          alignments and the attention_mechanism's values (memory).
        - Step 6: Calculate the attention output by concatenating the cell
          output and context through the attention layer (a linear layer with
          `attention_layer_size` outputs).

        Args:
          inputs: (Possibly nested tuple of) Tensor, the input at this time
            step.
          state: An instance of `AttentionWrapperState` containing
            tensors from the previous time step.
          **kwargs: Dict, other keyword arguments for the cell call method.

        Returns:
          A tuple `(attention_or_cell_output, next_state)`, where:

          - `attention_or_cell_output` depending on `output_attention`.
          - `next_state` is an instance of `AttentionWrapperState`
             containing the state calculated at this time step.

        Raises:
          TypeError: If `state` is not an instance of `AttentionWrapperState`.
        """
        if not isinstance(state, AttentionWrapperState):
            try:
                state = AttentionWrapperState(*state)
            except TypeError:
                raise TypeError(
                    "Expected state to be instance of AttentionWrapperState or "
                    "values that can construct AttentionWrapperState. "
                    "Received type %s instead." % type(state)
                )

        # Step 1: Calculate the true inputs to the cell based on the
        # previous attention value.
        cell_inputs = self._cell_input_fn(inputs, state.attention)
        cell_state = state.cell_state
        cell_output, next_cell_state = self._cell(cell_inputs, cell_state, **kwargs)

        cell_batch_size = (
            tf.compat.dimension_value(cell_output.shape[0]) or tf.shape(cell_output)[0]
        )
        error_message = (
            "When applying AttentionWrapper %s: " % self.name
            + "Non-matching batch sizes between the memory "
            "(encoder output) and the query (decoder output).  Are you using "
            "the BeamSearchDecoder?  You may need to tile your memory input "
            "via the tfa.seq2seq.tile_batch function with argument "
            "multiple=beam_width."
        )
        with tf.control_dependencies(
            self._batch_size_checks(cell_batch_size, error_message)
        ):  # pylint: disable=bad-continuation
            cell_output = tf.identity(cell_output, name="checked_cell_output")

        if self._is_multi:
            previous_attention_state = state.attention_state
            previous_alignment_history = state.alignment_history
        else:
            previous_attention_state = [state.attention_state]
            previous_alignment_history = [state.alignment_history]

        all_alignments = []
        all_attentions = []
        all_attention_states = []
        maybe_all_histories = []
        for i, attention_mechanism in enumerate(self._attention_mechanisms):
            attention, alignments, next_attention_state = self._attention_fn(
                attention_mechanism,
                cell_output,
                previous_attention_state[i],
                self._attention_layers[i] if self._attention_layers else None,
            )
            alignment_history = (
                previous_alignment_history[i].write(
                    previous_alignment_history[i].size(), alignments
                )
                if self._alignment_history
                else ()
            )

            all_attention_states.append(next_attention_state)
            all_alignments.append(alignments)
            all_attentions.append(attention)
            maybe_all_histories.append(alignment_history)

        attention = tf.concat(all_attentions, 1)
        next_state = AttentionWrapperState(
            cell_state=next_cell_state,
            attention=attention,
            attention_state=self._item_or_tuple(all_attention_states),
            alignments=self._item_or_tuple(all_alignments),
            alignment_history=self._item_or_tuple(maybe_all_histories),
        )

        if self._output_attention:
            return attention, next_state
        else:
            return cell_output, next_state