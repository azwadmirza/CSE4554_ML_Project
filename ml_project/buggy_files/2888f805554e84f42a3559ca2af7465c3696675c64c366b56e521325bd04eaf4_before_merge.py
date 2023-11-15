    def to_quantiles(self, out: Dict[str, torch.Tensor], quantiles=None):
        if quantiles is None:
            if self.quantiles is None:
                quantiles = [0.5]
            else:
                quantiles = self.quantiles
        predictions = super().to_prediction(out)
        return torch.stack([torch.tensor(scipy.stats.poisson(predictions).ppf(q)) for q in quantiles], dim=-1)