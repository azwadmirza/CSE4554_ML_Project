    def expand(self, batch_shape):
        batch_shape = torch.Size(batch_shape)
        return UniformPrior(self.low.expand(batch_shape), self.high.expand(batch_shape))