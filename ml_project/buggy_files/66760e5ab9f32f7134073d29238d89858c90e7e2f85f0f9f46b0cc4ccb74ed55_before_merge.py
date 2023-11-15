    def fit(self, y: pd.Series, X: pd.DataFrame):
        """
        Determine scales for each group

        Args:
            y (pd.Series): input data
            X (pd.DataFrame): dataframe with columns for each group defined in ``groups`` parameter.

        Returns:
            self
        """
        y = self._preprocess_y(y)
        if len(self.groups) == 0:
            assert not self.scale_by_group, "No groups are defined, i.e. `scale_by_group=[]`"
            if self.method == "standard":
                mean = np.mean(y)
                self.norm_ = mean, np.std(y) / (mean + self.eps)
            else:
                quantiles = np.quantile(y, [0.25, 0.5, 0.75])
                self.norm_ = quantiles[1], (quantiles[2] - quantiles[0]) / (quantiles[1] + self.eps)

        elif self.scale_by_group:
            if self.method == "standard":
                self.norm_ = {
                    g: X[[g]]
                    .assign(y=y)
                    .groupby(g, observed=True)
                    .agg(mean=("y", "mean"), scale=("y", "std"))
                    .assign(scale=lambda x: x.scale / (x["mean"] + self.eps))
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
                        median=lambda x: x[0.5] + self.eps,
                        scale=lambda x: (x[0.75] - x[0.25] + self.eps) / (x[0.5] + self.eps),
                    )[["median", "scale"]]
                    for g in self.groups
                }
            # calculate missings
            self.missing_ = {group: scales.median().to_dict() for group, scales in self.norm_.items()}

        else:
            if self.method == "standard":
                self.norm_ = (
                    X[self.groups]
                    .assign(y=y)
                    .groupby(self.groups, observed=True)
                    .agg(mean=("y", "mean"), scale=("y", "std"))
                    .assign(scale=lambda x: x.scale / (x["mean"] + self.eps))
                )
            else:
                self.norm_ = (
                    X[self.groups]
                    .assign(y=y)
                    .groupby(self.groups, observed=True)
                    .y.quantile([0.25, 0.5, 0.75])
                    .unstack(-1)
                    .assign(
                        median=lambda x: x[0.5] + self.eps,
                        scale=lambda x: (x[0.75] - x[0.25] + self.eps) / (x[0.5] + self.eps) / 2.0,
                    )[["median", "scale"]]
                )
            self.missing_ = self.norm_.median().to_dict()
        return self