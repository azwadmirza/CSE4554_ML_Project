    def load(cls, fname_or_handle, **kwargs):
        model = super(WordEmbeddingsKeyedVectors, cls).load(fname_or_handle, **kwargs)
        _try_upgrade(model)
        return model