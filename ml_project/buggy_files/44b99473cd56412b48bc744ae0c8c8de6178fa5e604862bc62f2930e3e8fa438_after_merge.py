    def __call__(self, a, index, value):
        return self.new_tensor([a], a.shape, indexes=index, value=value)