    def fit(self, y: Union[pd.Series, np.ndarray, torch.Tensor]):
        """
        Fit transformer, i.e. determine center and scale of data

        Args:
            y (Union[pd.Series, np.ndarray, torch.Tensor]): input data

        Returns:
            TorchNormalizer: self
        """
        y = self._preprocess_y(y)

        if self.method == "standard":
            if isinstance(y, torch.Tensor):
                self.center_ = torch.mean(y)
                self.scale_ = torch.std(y) / (self.center_ + self.eps)
            else:
                self.center_ = np.mean(y)
                self.scale_ = np.std(y) / (self.center_ + self.eps)

        elif self.method == "robust":
            if isinstance(y, torch.Tensor):
                self.center_ = torch.median(y)
                q_75 = y.kthvalue(int(len(y) * 0.75)).values
                q_25 = y.kthvalue(int(len(y) * 0.25)).values
            else:
                self.center_ = np.median(y)
                q_75 = np.percentiley(y, 75)
                q_25 = np.percentiley(y, 25)
            self.scale_ = (q_75 - q_25) / (self.center_ + self.eps) / 2.0
        return self