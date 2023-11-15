    def check(self, tensor):
        return torch.all(tensor <= self.upper_bound) and torch.all(tensor >= self.lower_bound)