    def state_size(self):
        """The `state_size` property of `AttentionWrapper`.

        Returns:
          An `AttentionWrapperState` tuple containing shapes used
          by this object.
        """
        return AttentionWrapperState(
            cell_state=self._cell.state_size,
            attention=self._get_attention_layer_size(),
            alignments=self._item_or_tuple(
                a.alignments_size for a in self._attention_mechanisms
            ),
            attention_state=self._item_or_tuple(
                a.state_size for a in self._attention_mechanisms
            ),
            alignment_history=self._item_or_tuple(
                a.alignments_size if self._alignment_history else ()
                for a in self._attention_mechanisms
            ),
        )  # sometimes a TensorArray