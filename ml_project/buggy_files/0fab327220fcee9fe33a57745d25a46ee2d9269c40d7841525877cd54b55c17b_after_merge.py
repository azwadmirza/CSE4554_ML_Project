    def save(self, *args, **kwargs):
        """Save complete model to disk, inherited from :class:`gensim.utils.SaveLoad`."""
        self._loss_grad = None  # Can't pickle autograd fn to disk
        attrs_to_ignore = ['_node_probabilities', '_node_counts_cumsum']
        kwargs['ignore'] = set(list(kwargs.get('ignore', [])) + attrs_to_ignore)
        super(PoincareModel, self).save(*args, **kwargs)