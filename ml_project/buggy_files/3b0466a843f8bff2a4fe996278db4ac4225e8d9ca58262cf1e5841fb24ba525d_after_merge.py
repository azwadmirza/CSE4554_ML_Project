    def fit(self, y: Union[pd.Series, np.ndarray, torch.Tensor]):
        """
        Fit transformer, i.e. determine center and scale of data

        Args:
            y (Union[pd.Series, np.ndarray, torch.Tensor]): input data

        Returns:
            TorchNormalizer: self
        """
        if self.coerce_positive is None and not self.log_scale:
            self.coerce_positive = (y >= 0).all()
        y = self._preprocess_y(y)

        if self.method == "standard":
            if isinstance(y, torch.Tensor):
                self.center_ = torch.mean(y, dim=-1) + self.eps
                self.scale_ = torch.std(y, dim=-1) + self.eps
            elif isinstance(y, np.ndarray):
                self.center_ = np.mean(y, axis=-1) + self.eps
                self.scale_ = np.std(y, axis=-1) + self.eps
            else:
                self.center_ = np.mean(y) + self.eps
                self.scale_ = np.std(y) + self.eps

        elif self.method == "robust":
            if isinstance(y, torch.Tensor):
                self.center_ = torch.median(y, dim=-1).values + self.eps
                q_75 = y.kthvalue(int(len(y) * 0.75), dim=-1).values
                q_25 = y.kthvalue(int(len(y) * 0.25), dim=-1).values
            elif isinstance(y, np.ndarray):
                self.center_ = np.median(y, axis=-1) + self.eps
                q_75 = np.percentiley(y, 75, axis=-1)
                q_25 = np.percentiley(y, 25, axis=-1)
            else:
                self.center_ = np.median(y) + self.eps
                q_75 = np.percentiley(y, 75)
                q_25 = np.percentiley(y, 25)
            self.scale_ = (q_75 - q_25) / 2.0 + self.eps
        if not self.center:
            self.scale_ = self.center_
            if isinstance(y, torch.Tensor):
                self.center_ = torch.zeros_like(self.center_)
            else:
                self.center_ = np.zeros_like(self.center_)
        return self