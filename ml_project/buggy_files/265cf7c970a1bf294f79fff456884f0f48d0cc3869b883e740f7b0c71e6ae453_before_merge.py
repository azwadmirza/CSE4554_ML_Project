  def fit_on_batch(self, X, y, w, variables=None, loss=None, callbacks=[]):
    """Perform a single step of training.

    Parameters
    ----------
    X: ndarray
      the inputs for the batch
    y: ndarray
      the labels for the batch
    w: ndarray
      the weights for the batch
    variables: list of tf.Variable
      the variables to train.  If None (the default), all trainable variables in
      the model are used.
    loss: function
      a function of the form f(outputs, labels, weights) that computes the loss
      for each batch.  If None (the default), the model's standard loss function
      is used.
    callbacks: function or list of functions
      one or more functions of the form f(model, step) that will be invoked after
      every step.  This can be used to perform validation, logging, etc.
   """
    if not self.built:
      self.build()
    dataset = NumpyDataset(X, y, w)
    return self.fit(
        dataset,
        nb_epoch=1,
        variables=variables,
        loss=loss,
        callbacks=callbacks)