    def __call__(self, data: Dict[str, torch.Tensor]) -> torch.Tensor:
        """
        Inverse transformation but with network output as input.

        Args:
            data (Dict[str, torch.Tensor]): Dictionary with entries
                * prediction: data to de-scale
                * target_scale: center and scale of data
            scale_only (bool): if to only scale prediction and not center it (even if `self.center is True`).
                Defaults to False.

        Returns:
            torch.Tensor: de-scaled data
        """
        # inverse transformation with tensors
        norm = data["target_scale"]

        # use correct shape for norm
        if data["prediction"].ndim > norm.ndim:
            norm = norm.unsqueeze(-1)

        # transform
        y_normed = data["prediction"] * norm[:, 1, None] + norm[:, 0, None]

        if self.log_scale:
            y_normed = (y_normed.exp() - self.log_zero_value).clamp_min(0.0)
        elif isinstance(self.coerce_positive, bool) and self.coerce_positive:
            y_normed = y_normed.clamp_min(0.0)
        elif isinstance(self.coerce_positive, float):
            y_normed = F.softplus(y_normed, beta=float(self.coerce_positive))

        # return correct shape
        if data["prediction"].ndim == 1 and y_normed.ndim > 1:
            y_normed = y_normed.squeeze(0)
        return y_normed