    def value_counts(self, normalize=False, sort=True, ascending=False,
                     bins=None, dropna=True):

        from functools import partial
        from pandas.tools.tile import cut
        from pandas.tools.merge import _get_join_indexers

        if bins is not None and not np.iterable(bins):
            # scalar bins cannot be done at top level
            # in a backward compatible way
            return self.apply(Series.value_counts,
                              normalize=normalize,
                              sort=sort,
                              ascending=ascending,
                              bins=bins)

        ids, _, _ = self.grouper.group_info
        val = self.obj.get_values()

        # groupby removes null keys from groupings
        mask = ids != -1
        ids, val = ids[mask], val[mask]

        if bins is None:
            lab, lev = algos.factorize(val, sort=True)
        else:
            cat, bins = cut(val, bins, retbins=True)
            # bins[:-1] for backward compat;
            # o.w. cat.categories could be better
            lab, lev, dropna = cat.codes, bins[:-1], False

        sorter = np.lexsort((lab, ids))
        ids, lab = ids[sorter], lab[sorter]

        # group boundries are where group ids change
        idx = np.r_[0, 1 + np.nonzero(ids[1:] != ids[:-1])[0]]

        # new values are where sorted labels change
        inc = np.r_[True, lab[1:] != lab[:-1]]
        inc[idx] = True  # group boundries are also new values
        out = np.diff(np.nonzero(np.r_[inc, True])[0]) # value counts

        # num. of times each group should be repeated
        rep = partial(np.repeat, repeats=np.add.reduceat(inc, idx))

        # multi-index components
        labels = list(map(rep, self.grouper.recons_labels)) + [lab[inc]]
        levels = [ping.group_index for ping in self.grouper.groupings] + [lev]
        names = self.grouper.names + [self.name]

        if dropna:
            mask = labels[-1] != -1
            if mask.all():
                dropna = False
            else:
                out, labels = out[mask], [label[mask] for label in labels]

        if normalize:
            out = out.astype('float')
            acc = rep(np.diff(np.r_[idx, len(ids)]))
            out /= acc[mask] if dropna else acc

        if sort and bins is None:
            cat = ids[inc][mask] if dropna else ids[inc]
            sorter = np.lexsort((out if ascending else -out, cat))
            out, labels[-1] = out[sorter], labels[-1][sorter]

        if bins is None:
            mi = MultiIndex(levels=levels, labels=labels, names=names,
                            verify_integrity=False)

            return Series(out, index=mi)

        # for compat. with algos.value_counts need to ensure every
        # bin is present at every index level, null filled with zeros
        diff = np.zeros(len(out), dtype='bool')
        for lab in labels[:-1]:
            diff |= np.r_[True, lab[1:] != lab[:-1]]

        ncat, nbin = diff.sum(), len(levels[-1])

        left = [np.repeat(np.arange(ncat), nbin),
                np.tile(np.arange(nbin), ncat)]

        right = [diff.cumsum() - 1, labels[-1]]

        _, idx = _get_join_indexers(left, right, sort=False, how='left')
        out = np.where(idx != -1, out[idx], 0)

        if sort:
            sorter = np.lexsort((out if ascending else -out, left[0]))
            out, left[-1] = out[sorter], left[-1][sorter]

        # build the multi-index w/ full levels
        labels = list(map(lambda lab: np.repeat(lab[diff], nbin), labels[:-1]))
        labels.append(left[-1])

        mi = MultiIndex(levels=levels, labels=labels, names=names,
                        verify_integrity=False)

        return Series(out, index=mi)