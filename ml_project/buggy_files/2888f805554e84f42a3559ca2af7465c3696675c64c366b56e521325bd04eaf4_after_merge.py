    def to_quantiles(self, y_pred: torch.Tensor) -> torch.Tensor:
        """
        Convert network prediction into a quantile prediction.

        Args:
            y_pred: prediction output of network (with ``output_type = samples``)

        Returns:
            torch.Tensor: prediction quantiles (last dimension)
        """
        samples = y_pred.size(-1)
        quantiles = torch.stack(
            [
                torch.kthvalue(y_pred, int(samples * q), dim=-1)[0] if samples > 1 else y_pred[..., 0]
                for q in self.quantiles
            ],
            dim=-1,
        )
        return quantiles