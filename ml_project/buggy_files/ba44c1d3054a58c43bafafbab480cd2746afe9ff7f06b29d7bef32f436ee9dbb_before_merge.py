    def nunique(self, dropna=True):
        """ Returns number of unique elements in the group """
        ids, _, _ = self.grouper.group_info
        val = self.obj.get_values()

        try:
            sorter = np.lexsort((val, ids))
        except TypeError:  # catches object dtypes
            assert val.dtype == object, \
                'val.dtype must be object, got %s' % val.dtype
            val, _ = algos.factorize(val, sort=False)
            sorter = np.lexsort((val, ids))
            _isnull = lambda a: a == -1
        else:
            _isnull = isnull

        ids, val = ids[sorter], val[sorter]

        # group boundaries are where group ids change
        # unique observations are where sorted values change
        idx = np.r_[0, 1 + np.nonzero(ids[1:] != ids[:-1])[0]]
        inc = np.r_[1, val[1:] != val[:-1]]

        # 1st item of each group is a new unique observation
        mask = _isnull(val)
        if dropna:
            inc[idx] = 1
            inc[mask] = 0
        else:
            inc[mask & np.r_[False, mask[:-1]]] = 0
            inc[idx] = 1

        out = np.add.reduceat(inc, idx).astype('int64', copy=False)
        res = out if ids[0] != -1 else out[1:]
        ri = self.grouper.result_index

        # we might have duplications among the bins
        if len(res) != len(ri):
            res, out = np.zeros(len(ri), dtype=out.dtype), res
            res[ids] = out

        return Series(res,
                      index=ri,
                      name=self.name)