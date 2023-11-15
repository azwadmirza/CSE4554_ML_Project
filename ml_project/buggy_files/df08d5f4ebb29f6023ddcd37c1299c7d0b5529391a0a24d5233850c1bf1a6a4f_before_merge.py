  def iterbatches(self,
                  batch_size=None,
                  epoch=0,
                  deterministic=False,
                  pad_batches=False):
    """Get an object that iterates over minibatches from the dataset.

    Each minibatch is returned as a tuple of four numpy arrays: (X, y,
    w, ids).
    """

    def iterate(dataset, batch_size, deterministic, pad_batches):
      n_samples = dataset._X_shape[0]
      if not deterministic:
        sample_perm = np.random.permutation(n_samples)
      else:
        sample_perm = np.arange(n_samples)
      if batch_size is None:
        batch_size = n_samples
      batch_idx = 0
      num_batches = np.math.ceil(n_samples / batch_size)
      while batch_idx < num_batches:
        start = batch_idx * batch_size
        end = min(n_samples, (batch_idx + 1) * batch_size)
        indices = range(start, end)
        perm_indices = sample_perm[indices]
        if isinstance(dataset._X, np.ndarray):
          X_batch = dataset._X[perm_indices]
        else:
          X_batch = dc.data.ImageLoader.load_img(
              [dataset._X[i] for i in perm_indices])
        if isinstance(dataset._y, np.ndarray):
          y_batch = dataset._y[perm_indices]
        else:
          y_batch = dc.data.ImageLoader.load_img(
              [dataset._y[i] for i in perm_indices])
        w_batch = dataset._w[perm_indices]
        ids_batch = dataset._ids[perm_indices]
        if pad_batches:
          (X_batch, y_batch, w_batch, ids_batch) = pad_batch(
              batch_size, X_batch, y_batch, w_batch, ids_batch)
        batch_idx += 1
        yield (X_batch, y_batch, w_batch, ids_batch)

    return iterate(self, batch_size, deterministic, pad_batches)