    def load(cls, fname_or_handle, **kwargs):
        model = super(WordEmbeddingsKeyedVectors, cls).load(fname_or_handle, **kwargs)
        if not hasattr(model, 'compatible_hash'):
            model.compatible_hash = False

        if hasattr(model, 'hash2index'):
            _rollback_optimization(model)

        return model