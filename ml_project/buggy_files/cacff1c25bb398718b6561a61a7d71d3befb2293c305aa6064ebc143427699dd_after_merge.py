    def transform(
        self, y: pd.Series, X: pd.DataFrame = None, return_norm: bool = False, target_scale: torch.Tensor = None
    ) -> Union[np.ndarray, Tuple[np.ndarray, np.ndarray]]:
        """
        Scale input data.

        Args:
            y (pd.Series): data to scale
            X (pd.DataFrame): dataframe with ``groups`` columns
            return_norm (bool, optional): If to return . Defaults to False.
            target_scale (torch.Tensor): target scale to use instead of fitted center and scale

        Returns:
            Union[np.ndarray, Tuple[np.ndarray, np.ndarray]]: Scaled data, if ``return_norm=True``, returns also scales
                as second element
        """
        if target_scale is None:
            assert X is not None, "either target_scale or X has to be passed"
            target_scale = self.get_norm(X)
        return super().transform(y=y, return_norm=return_norm, target_scale=target_scale)