    def get(self):
        """Just a pass through. This is most commonly used when calling .get() on a
        AutogradTensor which has also been shared."""
        tensor = self.child.get()

        if isinstance(tensor, torch.Tensor):
            # Remove the autograd node if a simple tensor is received
            if not tensor.is_wrapper:
                return tensor
            # If it's a wrapper, then insert the autograd under the wrapper
            else:
                self.child = tensor.child
                tensor.child = self
                return tensor

        self.child = tensor
        return self