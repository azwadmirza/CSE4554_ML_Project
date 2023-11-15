  def make_tf_dataset(self,
                      batch_size=100,
                      epochs=1,
                      deterministic=False,
                      pad_batches=False):
    """Create a tf.data.Dataset that iterates over the data in this Dataset.

    Each value returned by the Dataset's iterator is a tuple of (X, y,
    w) for one batch.

    Parameters
    ----------
    batch_size: int
      the number of samples to include in each batch
    epochs: int
      the number of times to iterate over the Dataset
    deterministic: bool
      if True, the data is produced in order.  If False, a different
      random permutation of the data is used for each epoch.
    pad_batches: bool
      if True, batches are padded as necessary to make the size of
      each batch exactly equal batch_size.

    Returns
    -------
    tf.Dataset that iterates over the same data.
    """
    # Retrieve the first sample so we can determine the dtypes.

    import tensorflow as tf
    X, y, w, ids = next(self.itersamples())
    dtypes = (tf.as_dtype(X.dtype), tf.as_dtype(y.dtype), tf.as_dtype(w.dtype))
    shapes = (tf.TensorShape([None] + list(X.shape)),
              tf.TensorShape([None] + list(y.shape)),
              tf.TensorShape([None] + list(w.shape)))

    # Create a Tensorflow Dataset.

    def gen_data():
      for X, y, w, ids in self.iterbatches(batch_size, epochs, deterministic,
                                           pad_batches):
        yield (X, y, w)

    return tf.data.Dataset.from_generator(gen_data, dtypes, shapes)