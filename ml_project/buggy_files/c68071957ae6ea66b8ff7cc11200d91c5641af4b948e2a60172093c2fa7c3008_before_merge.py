  def iterbatches(self,
                  batch_size=None,
                  epoch=0,
                  deterministic=False,
                  pad_batches=False):
    """ Get an object that iterates over minibatches from the dataset.

    It is guaranteed that the number of batches returned is
    `math.ceil(len(dataset)/batch_size)`. Each minibatch is returned as
    a tuple of four numpy arrays: `(X, y, w, ids)`.

    Parameters:
    -----------
    batch_size: int
      Number of elements in a batch. If None, then it yields batches
      with size equal to the size of each individual shard.
    epoch: int
      Not used
    deterministic: bool
      Whether or not we should should shuffle each shard before
      generating the batches.  Note that this is only local in the
      sense that it does not ever mix between different shards.
    pad_batches: bool
      Whether or not we should pad the last batch, globally, such that
      it has exactly batch_size elements.
    """
    shard_indices = list(range(self.get_number_shards()))
    return self._iterbatches_from_shards(shard_indices, batch_size,
                                         deterministic, pad_batches)