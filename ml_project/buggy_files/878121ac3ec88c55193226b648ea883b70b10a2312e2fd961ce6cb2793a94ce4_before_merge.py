    def mean(tensor: torch.Tensor) -> torch.Tensor:
        mask = tensor > tensor.mean()
        return mask