    def _part_ind(self, ptype):
        if self._particle_mask.get(ptype) is None:
            # If scipy is installed, use the fast KD tree
            # implementation. Else, fall back onto the direct
            # brute-force algorithm.
            try:
                _scipy.spatial.KDTree
                mask = self._part_ind_KDTree(ptype)
            except ImportError:
                mask = self._part_ind_brute_force(ptype)

            self._particle_mask[ptype] = mask
        return self._particle_mask[ptype]