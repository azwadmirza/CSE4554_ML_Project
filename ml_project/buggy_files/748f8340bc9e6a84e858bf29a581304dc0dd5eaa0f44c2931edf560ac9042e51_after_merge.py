  def serve_function(self):
    """Returns a function for serving this model.

    Returns:
      A ``tf.function``.
    """
    # Set name attribute of the input TensorSpec.
    input_signature = {
        name:tf.TensorSpec.from_spec(spec, name=name)
        for name, spec in self.features_inputter.input_signature().items()}

    @tf.function(input_signature=(input_signature,))
    def _run(features):
      features = self.features_inputter.make_features(features=features.copy())
      if isinstance(features, (list, tuple)):
        # Special case for unsupervised inputters that always return a tuple (features, labels).
        features = features[0]
      _, predictions = self(features)
      return predictions

    return _run