    def _symmetrize(self):
        """Word pairs may have been encountered in (i, j) and (j, i) order.
        Rather than enforcing a particular ordering during the update process,
        we choose to symmetrize the co-occurrence matrix after accumulation has completed.
        """
        co_occ = self._co_occurrences
        co_occ.setdiag(self._occurrences)  # diagonal should be equal to occurrence counts
        self._co_occurrences = co_occ + co_occ.T - sps.diags(co_occ.diagonal(), dtype='uint32')