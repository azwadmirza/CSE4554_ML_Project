    def cpu(self):
        """Move all self attributes to CPU."""
        self.to(torch.device("cpu"))