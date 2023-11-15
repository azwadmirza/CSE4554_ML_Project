    def load(cls, *args, **kwargs):
        """Load model from disk, inherited from :class:`~gensim.utils.SaveLoad`."""
        model = super(PoincareModel, cls).load(*args, **kwargs)
        model._init_node_probabilities()
        return model