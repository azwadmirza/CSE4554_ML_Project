    def get_parameters(self, *args, **kwargs) -> torch.Tensor:
        """
        Returns parameters that were used for encoding.

        Returns:
            torch.Tensor: First element is center of data and second is scale
        """
        return torch.stack([torch.as_tensor(self.center_), torch.as_tensor(self.scale_)], dim=-1)