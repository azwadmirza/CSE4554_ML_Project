    def __call__(self, a, index, value):
        return self.new_tensor([a, index, value], a.shape)