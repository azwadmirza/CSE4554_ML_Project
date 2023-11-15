  def iterbatches(self, **kwargs):
    """Loop through all internal datasets in the same order.

    Parameters
    ----------
    batch_size: int
      Number of samples from each dataset to return
    epochs: int
      Number of times to loop through the datasets
    pad_batches: boolean
      Should all batches==batch_size

    Returns
    -------
    Generator which yields a dictionary {key: dataset.X[batch]}
    """
    key_order = [x for x in self.datasets.keys()]
    if "epochs" in kwargs:
      epochs = kwargs['epochs']
      del kwargs['epochs']
    else:
      epochs = 1
    kwargs['deterministic'] = True
    for epoch in range(epochs):
      iterators = [self.datasets[x].iterbatches(**kwargs) for x in key_order]
      for tup in zip(*iterators):
        m_d = {key_order[i]: tup[i][0] for i in range(len(key_order))}
        yield m_d