    def _run(features):
      features = self.features_inputter.make_features(features=features.copy())
      if isinstance(features, (list, tuple)):
        # Special case for unsupervised inputters that always return a tuple (features, labels).
        features = features[0]
      _, predictions = self(features)
      return predictions