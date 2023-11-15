    def fit(self, y: pd.Series, X: pd.DataFrame):
        """
        Determine scales for each group

        Args:
            y (pd.Series): input data
            X (pd.DataFrame): dataframe with columns for each group defined in ``groups`` parameter.

        Returns:
            self
        """
        if self.coerce_positive is None and not self.log_scale:
            self.coerce_positive = (y >= 0).all()
        y = self._preprocess_y(y)
        if len(self.groups) == 0:
            assert not self.scale_by_group, "No groups are defined, i.e. `scale_by_group=[]`"
            if self.method == "standard":
                self.norm_ = [np.mean(y) + self.eps, np.std(y) + self.eps]  # center and scale
            else:
                quantiles = np.quantile(y, [0.25, 0.5, 0.75])
                self.norm_ = [
                    quantiles[1] + self.eps,
                    (quantiles[2] - quantiles[0]) / 2.0 + self.eps,
                ]  # center and scale
            if not self.center:
                self.norm_[1] = self.norm_[0]
                self.norm_[0] = 0.0

        elif self.scale_by_group:
            if self.method == "standard":
                self.norm_ = {
                    g: X[[g]]
                    .assign(y=y)
                    .groupby(g, observed=True)
                    .agg(center=("y", "mean"), scale=("y", "std"))
                    .assign(center=lambda x: x["center"] + self.eps, scale=lambda x: x.scale + self.eps)
                    for g in self.groups
                }
            else:
                self.norm_ = {
                    g: X[[g]]
                    .assign(y=y)
                    .groupby(g, observed=True)
                    .y.quantile([0.25, 0.5, 0.75])
                    .unstack(-1)
                    .assign(
                        center=lambda x: x[0.5] + self.eps,
                        scale=lambda x: (x[0.75] - x[0.25]) / 2.0 + self.eps,
                    )[["center", "scale"]]
                    for g in self.groups
                }
            # calculate missings
            if not self.center:  # swap center and scale

                def swap_parameters(norm):
                    norm["scale"] = norm["center"]
                    norm["center"] = 0.0
                    return norm

                self.norm = {g: swap_parameters(norm) for g, norm in self.norm_.items()}
            self.missing_ = {group: scales.median().to_dict() for group, scales in self.norm_.items()}

        else:
            if self.method == "standard":
                self.norm_ = (
                    X[self.groups]
                    .assign(y=y)
                    .groupby(self.groups, observed=True)
                    .agg(center=("y", "mean"), scale=("y", "std"))
                    .assign(center=lambda x: x["center"] + self.eps, scale=lambda x: x.scale + self.eps)
                )
            else:
                self.norm_ = (
                    X[self.groups]
                    .assign(y=y)
                    .groupby(self.groups, observed=True)
                    .y.quantile([0.25, 0.5, 0.75])
                    .unstack(-1)
                    .assign(
                        center=lambda x: x[0.5] + self.eps,
                        scale=lambda x: (x[0.75] - x[0.25]) / 2.0 + self.eps,
                    )[["center", "scale"]]
                )
            if not self.center:  # swap center and scale
                self.norm_["scale"] = self.norm_["center"]
                self.norm_["center"] = 0.0
            self.missing_ = self.norm_.median().to_dict()
        return self