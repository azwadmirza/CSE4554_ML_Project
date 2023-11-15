    def expand(self, batch_shape):
        return Normal.expand(self, batch_shape, _instance=self)