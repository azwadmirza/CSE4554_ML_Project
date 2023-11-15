    def _read_fixed_header(self):
        """
        Reads the fixed header of the Mini-SEED file and writes all entries to
        self.fixed_header, a dictionary.
        """
        # Init empty fixed header dictionary. Use an ordered dictionary to
        # achieve the same order as in the Mini-SEED manual.
        self.fixed_header = OrderedDict()
        # Read and unpack.
        self.file.seek(self.record_offset, 0)
        fixed_header = self.file.read(48)
        encoding = native_str('%s20c2H3Bx2H2h4Bl2h' % self.endian)
        try:
            header_item = unpack(encoding, fixed_header)
        except Exception:
            if len(fixed_header) == 0:
                msg = "Unexpected end of file."
                raise IOError(msg)
            raise
        # Write values to dictionary.
        self.fixed_header['Sequence number'] = \
            int(''.join(x.decode('ascii', errors="replace")
                for x in header_item[:6]))
        self.fixed_header['Data header/quality indicator'] = \
            header_item[6].decode('ascii', errors="replace")
        self.fixed_header['Station identifier code'] = \
            ''.join(x.decode('ascii', errors="replace")
                    for x in header_item[8:13]).strip()
        self.fixed_header['Location identifier'] = \
            ''.join(x.decode('ascii', errors="replace")
                    for x in header_item[13:15]).strip()
        self.fixed_header['Channel identifier'] = \
            ''.join(x.decode('ascii', errors="replace")
                    for x in header_item[15:18]).strip()
        self.fixed_header['Network code'] = \
            ''.join(x.decode('ascii', errors="replace")
                    for x in header_item[18:20]).strip()
        # Construct the starttime. This is only the starttime in the fixed
        # header without any offset. See page 31 of the SEED manual for the
        # time definition.
        self.fixed_header['Record start time'] = \
            UTCDateTime(year=header_item[20], julday=header_item[21],
                        hour=header_item[22], minute=header_item[23],
                        second=header_item[24], microsecond=header_item[25] *
                        100)
        self.fixed_header['Number of samples'] = int(header_item[26])
        self.fixed_header['Sample rate factor'] = int(header_item[27])
        self.fixed_header['Sample rate multiplier'] = int(header_item[28])
        self.fixed_header['Activity flags'] = int(header_item[29])
        self.fixed_header['I/O and clock flags'] = int(header_item[30])
        self.fixed_header['Data quality flags'] = int(header_item[31])
        self.fixed_header['Number of blockettes that follow'] = \
            int(header_item[32])
        self.fixed_header['Time correction'] = int(header_item[33])
        self.fixed_header['Beginning of data'] = int(header_item[34])
        self.fixed_header['First blockette'] = int(header_item[35])