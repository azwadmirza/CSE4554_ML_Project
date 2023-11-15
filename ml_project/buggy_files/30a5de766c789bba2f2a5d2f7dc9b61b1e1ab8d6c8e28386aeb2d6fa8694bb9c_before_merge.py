    def parse_array_definition(self):
        """Reads and returns the element type and length of the array.

        The position in the file must be just after the
        array encoded dtype.

        """
        self.skipif4()
        enc_eltype = iou.read_long(self.f, "big")
        self.skipif4()
        length = iou.read_long(self.f, "big")
        return length, enc_eltype