    def expand(self, batch_shape):
        batch_shape = torch.Size(batch_shape)
        return LogNormalPrior(self.loc.expand(batch_shape), self.scale.expand(batch_shape))