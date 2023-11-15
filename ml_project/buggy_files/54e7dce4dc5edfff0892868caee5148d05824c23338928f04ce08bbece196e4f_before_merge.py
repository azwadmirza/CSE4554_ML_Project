    def parse_tag_group(self, skip4=1):
        """Parse the root TagGroup of the given DM3 file f.
        Returns the tuple (is_sorted, is_open, n_tags).
        endian can be either 'big' or 'little'.
        """
        is_sorted = iou.read_byte(self.f, "big")
        is_open = iou.read_byte(self.f, "big")
        self.skipif4(n=skip4)
        n_tags = iou.read_long(self.f, "big")
        return bool(is_sorted), bool(is_open), n_tags