  def __call__(self, features, labels, params, mode, config=None):  # pylint: disable=arguments-differ
    """Calls the model function.

    Returns:
      outputs: The model outputs (usually unscaled probabilities).
        Optional if :obj:`mode` is ``tf.estimator.ModeKeys.PREDICT``.
      predictions: The model predictions.
        Optional if :obj:`mode` is ``tf.estimator.ModeKeys.TRAIN``.

    See Also:
      ``tf.estimator.Estimator`` 's ``model_fn`` argument for more details about
      the arguments of this function.
    """
    with tf.variable_scope(self.name, initializer=self._initializer(params)):
      return self._call(features, labels, params, mode)