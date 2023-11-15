    def expand(self, batch_shape):
        return LogNormal.expand(self, batch_shape, _instance=self)