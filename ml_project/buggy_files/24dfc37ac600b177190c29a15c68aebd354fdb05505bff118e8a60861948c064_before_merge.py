    def get(self):
        """Just a pass through. This is most commonly used when calling .get() on a
        AutogradTensor which has also been shared."""
        self.child = self.child.get()
        # Remove the autograd node if a simple tensor is received
        if isinstance(self.child, torch.Tensor) and not self.child.is_wrapper:
            return self.child
        return self