    def transform(
        self, y: Union[pd.Series, np.ndarray, torch.Tensor], return_norm: bool = False
    ) -> Union[Tuple[Union[np.ndarray, torch.Tensor], np.ndarray], Union[np.ndarray, torch.Tensor]]:
        """
        Rescale data.

        Args:
            y (Union[pd.Series, np.ndarray, torch.Tensor]): input data
            return_norm (bool, optional): [description]. Defaults to False.

        Returns:
            Union[Tuple[Union[np.ndarray, torch.Tensor], np.ndarray], Union[np.ndarray, torch.Tensor]]: rescaled
                data with type depending on input type. returns second element if ``return_norm=True``
        """
        if self.log_scale:
            if isinstance(y, torch.Tensor):
                y = (y + self.log_zero_value + self.eps).log()
            else:
                y = np.log(y + self.log_zero_value + self.eps)
        if self.center:
            y = (y / (self.center_ + self.eps) - 1) / (self.scale_ + self.eps)
        else:
            y = y / (self.center_ + self.eps)
        if return_norm:
            return y, self.get_parameters().numpy()[None, :]
        else:
            return y