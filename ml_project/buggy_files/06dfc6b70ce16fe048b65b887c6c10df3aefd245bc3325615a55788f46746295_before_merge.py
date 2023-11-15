    def gen_data():
      for epoch in range(epochs):
        for X, y, w, ids in self.iterbatches(batch_size, epoch, deterministic,
                                             pad_batches):
          yield (X, y, w)