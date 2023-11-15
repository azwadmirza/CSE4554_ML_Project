    def gen_data():
      for X, y, w, ids in self.iterbatches(batch_size, epochs, deterministic,
                                           pad_batches):
        yield (X, y, w)