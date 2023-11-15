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
      _, predictions = self(features)
      return predictions

    return _run