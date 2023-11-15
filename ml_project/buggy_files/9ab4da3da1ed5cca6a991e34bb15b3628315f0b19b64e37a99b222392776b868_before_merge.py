    def _run(features):
      features = self.features_inputter.make_features(features=features.copy())
      _, predictions = self(features)
      return predictions