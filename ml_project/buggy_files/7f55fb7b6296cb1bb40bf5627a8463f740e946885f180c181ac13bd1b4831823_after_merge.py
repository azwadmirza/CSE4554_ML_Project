    def __eq__(self, other):
        """Compare `self` and `other` for equality.

        Returns
        -------
        bool
            The result if `self` and `other` are the same class
        NotImplemented
            If `other` is not the same class as `self` then returning
            NotImplemented delegates the result to superclass.__eq__(subclass)
        """
        # When comparing against self this will be faster
        if other is self:
            return True

        if isinstance(other, self.__class__):
            # Compare Elements using values()
            # Convert values() to a list for compatibility between
            #   python 2 and 3
            # Sort values() by element tag
            self_elem = sorted(list(self._dict.values()), key=lambda x: x.tag)
            other_elem = sorted(list(other._dict.values()), key=lambda x: x.tag)
            return self_elem == other_elem

        return NotImplemented