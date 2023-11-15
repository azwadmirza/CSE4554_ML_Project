  def create_variables(self, optimizer=None):
    """Creates the model variables by running it once.

    Args:
      optimizer: If set, also create the optimizer variables.
    """
    if self.built:
      return

    # Create input features from the input signatures. We remove the leading
    # batch dimension as sometimes assumed by make_features methods and set
    # unspecified dimensions to 1.
    features = tf.nest.map_structure(
        lambda spec: tf.fill(
            [dim or 1 for dim in spec.shape.as_list()[1:]],
            tf.constant("" if spec.dtype is tf.string else 1, dtype=spec.dtype)),
        self.examples_inputter.input_signature())
    features = self.examples_inputter.make_features(features=features, training=True)

    # Add the batch dimension back before calling the model.
    features, labels = tf.nest.map_structure(lambda x: tf.expand_dims(x, 0), features)
    _ = self(features, labels=labels, training=True, step=0)

    if optimizer is not None:
      _ = optimizer.iterations
      optimizer._create_hypers()  # pylint: disable=protected-access
      optimizer._create_slots(self.trainable_variables)  # pylint: disable=protected-access