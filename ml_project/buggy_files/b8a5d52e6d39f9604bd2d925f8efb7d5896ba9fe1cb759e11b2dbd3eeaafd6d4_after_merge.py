    def expand(self, batch_shape):
        batch_shape = torch.Size(batch_shape)
        return GammaPrior(self.concentration.expand(batch_shape), self.rate.expand(batch_shape))