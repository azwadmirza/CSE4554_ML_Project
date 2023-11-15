    def _part_ind(self, ptype):
        # If scipy is installed, use the fast KD tree
        # implementation. Else, fall back onto the direct
        # brute-force algorithm.
        try:
            _scipy.spatial.KDTree
            return self._part_ind_KDTree(ptype)
        except ImportError:
            return self._part_ind_brute_force(ptype)