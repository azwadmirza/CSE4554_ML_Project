    def forward(self, init_features: Tensor) -> Tensor:  # type: ignore[override]
        features = [init_features]
        for name, layer in self.items():
            new_features = layer(features)
            features.append(new_features)
        return torch.cat(features, 1)