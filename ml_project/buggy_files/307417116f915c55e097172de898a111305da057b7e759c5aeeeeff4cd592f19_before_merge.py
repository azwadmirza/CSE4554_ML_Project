    def _get_hvals(self):
        # The entries in this header are capitalized and named to match Table 4
        # in the GADGET-2 user guide.
        gformat = _get_gadget_format(self.parameter_filename)
        f = open(self.parameter_filename, 'rb')
        if gformat[0] == 2:
            f.seek(f.tell() + SNAP_FORMAT_2_OFFSET)
        hvals = read_record(f, self._header_spec, endian=gformat[1])
        for i in hvals:
            if len(hvals[i]) == 1:
                hvals[i] = hvals[i][0]
        return hvals