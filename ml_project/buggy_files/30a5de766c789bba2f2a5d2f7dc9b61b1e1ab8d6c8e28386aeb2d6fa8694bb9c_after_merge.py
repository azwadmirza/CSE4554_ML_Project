    def parse_array_definition(self):
        """Reads and returns the element type and length of the array.

        The position in the file must be just after the
        array encoded dtype.

        """
        enc_eltype = self.read_l_or_q(self.f, "big")
        length = self.read_l_or_q(self.f, "big")
        return length, enc_eltype