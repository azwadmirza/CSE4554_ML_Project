    def embedding_length(self) -> int:
        """Returns the length of the embedding vector."""

        if not self.layer_mean:
            length = len(self.layer_indexes) * self.model.config.hidden_size
        else:
            length = self.model.config.hidden_size

        if self.pooling_operation == 'first_last': length *= 2

        return length