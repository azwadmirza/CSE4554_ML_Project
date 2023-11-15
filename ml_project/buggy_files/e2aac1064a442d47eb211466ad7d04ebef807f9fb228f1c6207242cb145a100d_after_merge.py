    def _slice(self, idx):
        with self.activate_file:
            start, stop, step = idx.indices(len(self))
            sliced = ndarray.NDArray(model=self.model, vars=self.vars)
            sliced.chain = self.chain
            sliced.samples = {v: self.samples[v][start:stop:step]
                              for v in self.varnames}
            sliced.draw_idx = (stop - start) // step
            return sliced