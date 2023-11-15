    def interpolate(self, method='pad', axis=0, inplace=False):
        values = self.values if inplace else self.values.copy()

        if values.ndim != 2:
            raise NotImplementedError

        transf = (lambda x: x) if axis == 0 else (lambda x: x.T)

        if method == 'pad':
            _pad(transf(values))
        else:
            _backfill(transf(values))

        return make_block(values, self.items, self.ref_items)