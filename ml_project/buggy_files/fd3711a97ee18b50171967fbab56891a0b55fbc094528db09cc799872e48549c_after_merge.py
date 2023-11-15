    def __getstate__(self):
        # special handling for serializing transformer models
        config_state_dict = self.model.config.__dict__
        model_state_dict = self.model.state_dict()

        # serialize the transformer models and the constructor arguments (but nothing else)
        model_state = {
            "config_state_dict": config_state_dict,
            "model_state_dict": model_state_dict,
            "embedding_length_internal": self.embedding_length,

            "name": self.name,
            "layer_indexes": self.layer_indexes,
            "subtoken_pooling": self.pooling_operation,
            "context_length": self.context_length,
            "layer_mean": self.layer_mean,
            "fine_tune": self.fine_tune,
            "allow_long_sentences": self.allow_long_sentences,
            "memory_effective_training": self.memory_effective_training,
            "respect_document_boundaries": self.respect_document_boundaries,
        }

        return model_state