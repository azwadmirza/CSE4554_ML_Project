    def __le__(self, other):
        """Implement the less-than or equal operand."""
        if hasattr(other, "alphabet"):
            if not Alphabet._check_type_compatible([self.alphabet,
                                                    other.alphabet]):
                warnings.warn("Incompatible alphabets {0!r} and {1!r}".format(
                              self.alphabet, other.alphabet),
                              BiopythonWarning)
            if isinstance(other, MutableSeq):
                return self.data <= other.data
        return str(self) <= str(other)