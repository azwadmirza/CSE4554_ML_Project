  def fit_on_batch(self,
                   X,
                   y,
                   w,
                   variables=None,
                   loss=None,
                   callbacks=[],
                   checkpoint=True,
                   max_checkpoints_to_keep=5):
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
    checkpoint: bool
      if true, save a checkpoint after performing the training step
    max_checkpoints_to_keep: int
      the maximum number of checkpoints to keep.  Older checkpoints are discarded.
    """
    self._ensure_built()
    dataset = NumpyDataset(X, y, w)
    return self.fit(
        dataset,
        nb_epoch=1,
        max_checkpoints_to_keep=max_checkpoints_to_keep,
        checkpoint_interval=self._global_step.numpy() + 2 if checkpoint else 0,
        variables=variables,
        loss=loss,
        callbacks=callbacks)