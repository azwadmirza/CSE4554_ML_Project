    def parse_string_definition(self):
        """Reads and returns the length of the string.

        The position in the file must be just after the
        string encoded dtype.
        """
        return self.read_l_or_q(self.f, "big")