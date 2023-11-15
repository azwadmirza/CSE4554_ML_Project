  def iterbatches(self,
                  batch_size=None,
                  epochs=1,
                  deterministic=False,
                  pad_batches=False):
    """Get an object that iterates over minibatches from the dataset.

    Each minibatch is returned as a tuple of four numpy arrays: `(X,
    y, w, ids)`.

    Parameters
    ----------
    batch_size: int, optional
      Number of elements in each batch
    epochs: int, optional
      Number of epochs to walk over dataset
    deterministic: bool, optional
      If True, follow deterministic order.
    pad_batches: bool, optional
      If True, pad each batch to `batch_size`.

    Returns
    -------
    Generator which yields tuples of four numpy arrays `(X, y, w, ids)`
    """
    raise NotImplementedError()