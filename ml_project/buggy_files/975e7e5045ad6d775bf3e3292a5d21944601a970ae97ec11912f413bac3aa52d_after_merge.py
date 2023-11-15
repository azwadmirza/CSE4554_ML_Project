    def expand(self, expand_shape, _instance=None):
        batch_shape = torch.Size(expand_shape)
        return HorseshoePrior(self.scale.expand(batch_shape))