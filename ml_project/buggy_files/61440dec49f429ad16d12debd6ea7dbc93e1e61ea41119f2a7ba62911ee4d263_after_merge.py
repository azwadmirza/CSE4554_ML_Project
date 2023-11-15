    def parse_struct_definition(self):
        """Reads and returns the struct definition tuple.

        The position in the file must be just after the
        struct encoded dtype.

        """
        length = self.read_l_or_q(self.f, "big")
        nfields = self.read_l_or_q(self.f, "big")
        definition = ()
        for ifield in range(nfields):
            length2 = self.read_l_or_q(self.f, "big")
            definition += (self.read_l_or_q(self.f, "big"),)

        return definition