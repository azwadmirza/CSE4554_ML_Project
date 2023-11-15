    def _slice(self, idx):
        with self.activate_file:
            if idx.start is None:
                burn = 0
            else:
                burn = idx.start
            if idx.step is None:
                thin = 1
            else:
                thin = idx.step

            sliced = ndarray.NDArray(model=self.model, vars=self.vars)
            sliced.chain = self.chain
            sliced.samples = {v: self.get_values(v, burn=burn, thin=thin)
                              for v in self.varnames}
            return sliced