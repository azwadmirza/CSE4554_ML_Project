    def _getitem_lowerdim(self, tup):
        from pandas.core.frame import DataFrame

        ax0 = self.obj._get_axis(0)
        # a bit kludgy
        if isinstance(ax0, MultiIndex):
            try:
                return self._get_label(tup, axis=0)
            except TypeError:
                # slices are unhashable
                pass
            except Exception:
                if isinstance(tup[0], slice):
                    raise IndexingError
                if tup[0] not in ax0:
                    raise

        # to avoid wasted computation
        # df.ix[d1:d2, 0] -> columns first (True)
        # df.ix[0, ['C', 'B', A']] -> rows first (False)
        for i, key in enumerate(tup):
            if _is_label_like(key):
                section = self._getitem_axis(key, axis=i)

                # might have been a MultiIndex
                if section.ndim == self.ndim:
                    new_key = tup[:i] + (_NS,) + tup[i+1:]
                    # new_key = tup[:i] + tup[i+1:]
                else:
                    new_key = tup[:i] + tup[i+1:]

                    # unfortunately need an odious kludge here because of
                    # DataFrame transposing convention
                    if (isinstance(section, DataFrame) and i > 0
                        and len(new_key) == 2):
                        a, b = new_key
                        new_key = b, a

                    if len(new_key) == 1:
                        new_key, = new_key

                return section.ix[new_key]

        raise IndexingError('not applicable')