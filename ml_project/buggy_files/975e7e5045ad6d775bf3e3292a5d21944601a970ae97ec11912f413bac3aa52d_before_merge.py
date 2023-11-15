    def expand(self, expand_shape, _instance=None):
        new = self._get_checked_instance(HorseshoePrior)
        batch_shape = torch.Size(expand_shape)
        new.scale = self.scale.expand(batch_shape)
        super(Distribution, new).__init__(batch_shape)
        new._validate_args = self._validate_args
        return new