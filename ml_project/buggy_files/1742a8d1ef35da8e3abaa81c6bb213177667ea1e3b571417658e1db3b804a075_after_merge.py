    def atoms(self):
        """An :class:`AtomGroup` of :class:`Atoms<Atom>` present in this
        :class:`ResidueGroup`.

        The :class:`Atoms<Atom>` are ordered locally by :class:`Residue` in the
        :class:`ResidueGroup`.  Duplicates are *not* removed.
        """
        # If indices is an empty list np.concatenate will fail (Issue #1999).
        try:
            ag = self.universe.atoms[np.concatenate(self.indices)]
        except ValueError:
            ag = self.universe.atoms[self.indices]
        # If the ResidueGroup is known to be unique, this also holds for the
        # atoms therein, since atoms can only belong to one residue at a time.
        # On the contrary, if the ResidueGroup is not unique, this does not
        # imply non-unique atoms, since residues might be empty.
        try:
            if self._cache['isunique']:
                ag._cache['isunique'] = True
                ag._cache['unique'] = ag
        except KeyError:
            pass
        return ag