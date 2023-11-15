    def save(self, *args, **kwargs):
        """Save complete model to disk, inherited from :class:`gensim.utils.SaveLoad`."""
        self._loss_grad = None  # Can't pickle autograd fn to disk
        super(PoincareModel, self).save(*args, **kwargs)