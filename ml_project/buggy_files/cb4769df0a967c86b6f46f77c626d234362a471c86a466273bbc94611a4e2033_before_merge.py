    def cpu(self):
        """Move all self attributes to CPU."""
        for k, v in self.items():
            if isinstance(v, torch.Tensor):
                self.__setitem__(k, v.cpu())