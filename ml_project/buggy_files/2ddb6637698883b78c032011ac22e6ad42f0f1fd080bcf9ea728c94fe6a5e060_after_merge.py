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
        if isinstance(other, (str, Seq, UnknownSeq)):
            return str(self) <= str(other)
        raise TypeError("'<=' not supported between instances of '{}' and '{}'"
                        .format(type(self).__name__, type(other).__name__))