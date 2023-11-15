    def to_prediction(self, y_pred: torch.Tensor) -> torch.Tensor:
        """
        Convert network prediction into a point prediction.

        Args:
            y_pred: prediction output of network (with ``output_type = samples``)

        Returns:
            torch.Tensor: mean prediction
        """
        return y_pred.mean(-1)