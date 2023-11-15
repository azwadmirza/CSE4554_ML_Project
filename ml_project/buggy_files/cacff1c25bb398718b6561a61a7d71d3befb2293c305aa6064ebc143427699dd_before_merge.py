    def transform(
        self, y: pd.Series, X: pd.DataFrame, return_norm: bool = False
    ) -> Union[np.ndarray, Tuple[np.ndarray, np.ndarray]]:
        """
        Scale input data.

        Args:
            y (pd.Series): data to scale
            X (pd.DataFrame): dataframe with ``groups`` columns
            return_norm (bool, optional): If to return . Defaults to False.

        Returns:
            Union[np.ndarray, Tuple[np.ndarray, np.ndarray]]: Scaled data, if ``return_norm=True``, returns also scales
                as second element
        """
        norm = self.get_norm(X)
        y = self._preprocess_y(y)
        if self.center:
            y_normed = (y / (norm[:, 0] + self.eps) - 1) / (norm[:, 1] + self.eps)
        else:
            y_normed = y / (norm[:, 0] + self.eps)
        if return_norm:
            return y_normed, norm
        else:
            return y_normed