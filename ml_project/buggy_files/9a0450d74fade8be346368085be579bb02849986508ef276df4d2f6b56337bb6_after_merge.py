    def atoms(self):
        """An :class:`AtomGroup` of :class:`Atoms<Atom>` present in this
        :class:`SegmentGroup`.

        The :class:`Atoms<Atom>` are ordered locally by :class:`Residue`, which
        are further ordered by :class:`Segment` in the :class:`SegmentGroup`.
        Duplicates are *not* removed.
        """
        # If indices is an empty list np.concatenate will fail (Issue #1999).
        try:
            ag = self.universe.atoms[np.concatenate(self.indices)]
        except ValueError:
            ag = self.universe.atoms[self.indices]
        # If the SegmentGroup is known to be unique, this also holds for the
        # residues therein, and thus, also for the atoms in those residues.
        # On the contrary, if the SegmentGroup is not unique, this does not
        # imply non-unique atoms, since segments or residues might be empty.
        try:
            if self._cache['isunique']:
                ag._cache['isunique'] = True
                ag._cache['unique'] = ag
        except KeyError:
            pass
        return ag