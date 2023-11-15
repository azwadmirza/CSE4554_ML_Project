    def parse_tag_group(self, size=False):
        """Parse the root TagGroup of the given DM3 file f.
        Returns the tuple (is_sorted, is_open, n_tags).
        endian can be either 'big' or 'little'.
        """
        is_sorted = iou.read_byte(self.f, "big")
        is_open = iou.read_byte(self.f, "big")
        if self.dm_version == 4 and size:
            # Just guessing that this is the size
            size = self.read_l_or_q(self.f, "big")
        n_tags = self.read_l_or_q(self.f, "big")
        return bool(is_sorted), bool(is_open), n_tags