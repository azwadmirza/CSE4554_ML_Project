    def embedding_length(self) -> int:

        if "embedding_length_internal" in self.__dict__.keys():
            return self.embedding_length_internal

        # """Returns the length of the embedding vector."""
        if not self.layer_mean:
            length = len(self.layer_indexes) * self.model.config.hidden_size
        else:
            length = self.model.config.hidden_size

        if self.pooling_operation == 'first_last': length *= 2

        self.__embedding_length = length

        return length