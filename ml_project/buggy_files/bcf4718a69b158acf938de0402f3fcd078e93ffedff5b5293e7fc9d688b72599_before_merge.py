    def __call__(self, a, index, shape):
        return self.new_tensor([a, index], shape)