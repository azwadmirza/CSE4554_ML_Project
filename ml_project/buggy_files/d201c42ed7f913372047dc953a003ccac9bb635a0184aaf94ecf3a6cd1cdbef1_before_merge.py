    def parse_string_definition(self):
        """Reads and returns the length of the string.

        The position in the file must be just after the
        string encoded dtype.
        """
        self.skipif4()
        return iou.read_long(self.f, "big")