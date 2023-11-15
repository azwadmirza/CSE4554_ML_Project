    def expand(self, batch_shape):
        batch_shape = torch.Size(batch_shape)
        return NormalPrior(self.loc.expand(batch_shape), self.scale.expand(batch_shape))