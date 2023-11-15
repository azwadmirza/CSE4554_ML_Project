    def parse_struct_definition(self):
        """Reads and returns the struct definition tuple.

        The position in the file must be just after the
        struct encoded dtype.

        """
        self.f.seek(4, 1)  # Skip the name length
        self.skipif4(2)
        nfields = iou.read_long(self.f, "big")
        definition = ()
        for ifield in range(nfields):
            self.f.seek(4, 1)
            self.skipif4(2)
            definition += (iou.read_long(self.f, "big"),)

        return definition