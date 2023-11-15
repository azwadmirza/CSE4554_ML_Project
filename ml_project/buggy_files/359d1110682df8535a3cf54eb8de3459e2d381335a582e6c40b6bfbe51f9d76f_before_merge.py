    def _partial_tup_index(self, tup, side='left'):
        if len(tup) > self.lexsort_depth:
            raise KeyError('Key length (%d) was greater than MultiIndex'
                           ' lexsort depth (%d)' %
                           (len(tup), self.lexsort_depth))

        n = len(tup)
        start, end = 0, len(self)
        zipped = zip(tup, self.levels, self.labels)
        for k, (lab, lev, labs) in enumerate(zipped):
            section = labs[start:end]

            if lab not in lev:
                if not lev.is_type_compatible(lib.infer_dtype([lab])):
                    raise TypeError('Level type mismatch: %s' % lab)

                # short circuit
                loc = lev.searchsorted(lab, side=side)
                if side == 'right' and loc >= 0:
                    loc -= 1
                return start + section.searchsorted(loc, side=side)

            idx = lev.get_loc(lab)
            if k < n - 1:
                end = start + section.searchsorted(idx, side='right')
                start = start + section.searchsorted(idx, side='left')
            else:
                return start + section.searchsorted(idx, side=side)