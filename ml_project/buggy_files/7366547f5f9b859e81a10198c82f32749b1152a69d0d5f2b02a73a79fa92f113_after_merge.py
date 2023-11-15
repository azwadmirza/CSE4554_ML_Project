    def interpolate(self, method='pad', axis=0, inplace=False,
                    limit=None, missing=None):
        values = self.values if inplace else self.values.copy()

        if values.ndim != 2:
            raise NotImplementedError

        transf = (lambda x: x) if axis == 0 else (lambda x: x.T)

        if missing is None:
            mask = None
        else: # todo create faster fill func without masking
            mask = _mask_missing(transf(values), missing)

        if method == 'pad':
            com.pad_2d(transf(values), limit=limit, mask=mask)
        else:
            com.backfill_2d(transf(values), limit=limit, mask=mask)

        return make_block(values, self.items, self.ref_items)