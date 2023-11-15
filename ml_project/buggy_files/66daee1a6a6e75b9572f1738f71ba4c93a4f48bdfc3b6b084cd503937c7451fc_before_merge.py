    def _preprocess_y(self, y: Union[pd.Series, np.ndarray, torch.Tensor]) -> Union[np.ndarray, torch.Tensor]:
        """
        Preprocess input data (e.g. take log).

        Can set coerce positive to a value if it was set to None and log_scale to False.

        Returns:
            Union[np.ndarray, torch.Tensor]: return rescaled series with type depending on input type
        """
        if self.coerce_positive is None and not self.log_scale:
            self.coerce_positive = (y >= 0).all()

        if self.log_scale:
            if isinstance(y, torch.Tensor):
                y = torch.log(y + self.log_zero_value)
            else:
                y = np.log(y + self.log_zero_value)
        return y