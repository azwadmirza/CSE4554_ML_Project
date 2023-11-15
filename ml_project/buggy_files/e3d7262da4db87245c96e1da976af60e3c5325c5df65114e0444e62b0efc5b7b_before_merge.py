    def _read_header(self):
        first_char = self.path_or_buf.read(1)
        if struct.unpack('c', first_char)[0] == b'<':
            # format 117 or higher (XML like)
            self.path_or_buf.read(27)  # stata_dta><header><release>
            self.format_version = int(self.path_or_buf.read(3))
            if self.format_version not in [117]:
                raise ValueError("Version of given Stata file is not 104, "
                                 "105, 108, 113 (Stata 8/9), 114 (Stata "
                                 "10/11), 115 (Stata 12) or 117 (Stata 13)")
            self.path_or_buf.read(21)  # </release><byteorder>
            self.byteorder = self.path_or_buf.read(3) == "MSF" and '>' or '<'
            self.path_or_buf.read(15)  # </byteorder><K>
            self.nvar = struct.unpack(self.byteorder + 'H',
                                      self.path_or_buf.read(2))[0]
            self.path_or_buf.read(7)  # </K><N>
            self.nobs = struct.unpack(self.byteorder + 'I',
                                      self.path_or_buf.read(4))[0]
            self.path_or_buf.read(11)  # </N><label>
            strlen = struct.unpack('b', self.path_or_buf.read(1))[0]
            self.data_label = self._null_terminate(self.path_or_buf.read(strlen))
            self.path_or_buf.read(19)  # </label><timestamp>
            strlen = struct.unpack('b', self.path_or_buf.read(1))[0]
            self.time_stamp = self._null_terminate(self.path_or_buf.read(strlen))
            self.path_or_buf.read(26)  # </timestamp></header><map>
            self.path_or_buf.read(8)  # 0x0000000000000000
            self.path_or_buf.read(8)  # position of <map>
            seek_vartypes = struct.unpack(
                self.byteorder + 'q', self.path_or_buf.read(8))[0] + 16
            seek_varnames = struct.unpack(
                self.byteorder + 'q', self.path_or_buf.read(8))[0] + 10
            seek_sortlist = struct.unpack(
                self.byteorder + 'q', self.path_or_buf.read(8))[0] + 10
            seek_formats = struct.unpack(
                self.byteorder + 'q', self.path_or_buf.read(8))[0] + 9
            seek_value_label_names = struct.unpack(
                self.byteorder + 'q', self.path_or_buf.read(8))[0] + 19
            seek_variable_labels = struct.unpack(
                self.byteorder + 'q', self.path_or_buf.read(8))[0] + 17
            self.path_or_buf.read(8)  # <characteristics>
            self.data_location = struct.unpack(
                self.byteorder + 'q', self.path_or_buf.read(8))[0] + 6
            self.seek_strls = struct.unpack(
                self.byteorder + 'q', self.path_or_buf.read(8))[0] + 7
            self.seek_value_labels = struct.unpack(
                self.byteorder + 'q', self.path_or_buf.read(8))[0] + 14
            #self.path_or_buf.read(8)  # </stata_dta>
            #self.path_or_buf.read(8)  # EOF
            self.path_or_buf.seek(seek_vartypes)
            typlist = [struct.unpack(self.byteorder + 'H',
                                     self.path_or_buf.read(2))[0]
                       for i in range(self.nvar)]
            self.typlist = [None]*self.nvar
            try:
                i = 0
                for typ in typlist:
                    if typ <= 2045 or typ == 32768:
                        self.typlist[i] = None
                    else:
                        self.typlist[i] = self.TYPE_MAP_XML[typ]
                    i += 1
            except:
                raise ValueError("cannot convert stata types [{0}]"
                                 .format(','.join(typlist)))
            self.dtyplist = [None]*self.nvar
            try:
                i = 0
                for typ in typlist:
                    if typ <= 2045:
                        self.dtyplist[i] = str(typ)
                    else:
                        self.dtyplist[i] = self.DTYPE_MAP_XML[typ]
                    i += 1
            except:
                raise ValueError("cannot convert stata dtypes [{0}]"
                                 .format(','.join(typlist)))

            self.path_or_buf.seek(seek_varnames)
            self.varlist = [self._null_terminate(self.path_or_buf.read(33))
                            for i in range(self.nvar)]

            self.path_or_buf.seek(seek_sortlist)
            self.srtlist = struct.unpack(
                self.byteorder + ('h' * (self.nvar + 1)),
                self.path_or_buf.read(2 * (self.nvar + 1))
            )[:-1]

            self.path_or_buf.seek(seek_formats)
            self.fmtlist = [self._null_terminate(self.path_or_buf.read(49))
                            for i in range(self.nvar)]

            self.path_or_buf.seek(seek_value_label_names)
            self.lbllist = [self._null_terminate(self.path_or_buf.read(33))
                            for i in range(self.nvar)]

            self.path_or_buf.seek(seek_variable_labels)
            self.vlblist = [self._null_terminate(self.path_or_buf.read(81))
                            for i in range(self.nvar)]
        else:
            # header
            self.format_version = struct.unpack('b', first_char)[0]
            if self.format_version not in [104, 105, 108, 113, 114, 115]:
                raise ValueError("Version of given Stata file is not 104, "
                                 "105, 108, 113 (Stata 8/9), 114 (Stata "
                                 "10/11), 115 (Stata 12) or 117 (Stata 13)")
            self.byteorder = struct.unpack('b', self.path_or_buf.read(1))[0] == 0x1 and '>' or '<'
            self.filetype = struct.unpack('b', self.path_or_buf.read(1))[0]
            self.path_or_buf.read(1)  # unused

            self.nvar = struct.unpack(self.byteorder + 'H',
                                      self.path_or_buf.read(2))[0]
            self.nobs = struct.unpack(self.byteorder + 'I',
                                      self.path_or_buf.read(4))[0]
            if self.format_version > 105:
                self.data_label = self._null_terminate(self.path_or_buf.read(81))
            else:
                self.data_label = self._null_terminate(self.path_or_buf.read(32))
            if self.format_version > 104:
                self.time_stamp = self._null_terminate(self.path_or_buf.read(18))

            # descriptors
            if self.format_version > 108:
                typlist = [ord(self.path_or_buf.read(1))
                           for i in range(self.nvar)]
            else:
                typlist = [
                    self.OLD_TYPE_MAPPING[
                        self._decode_bytes(self.path_or_buf.read(1))
                    ] for i in range(self.nvar)
                ]

            try:
                self.typlist = [self.TYPE_MAP[typ] for typ in typlist]
            except:
                raise ValueError("cannot convert stata types [{0}]"
                                 .format(','.join(typlist)))
            try:
                self.dtyplist = [self.DTYPE_MAP[typ] for typ in typlist]
            except:
                raise ValueError("cannot convert stata dtypes [{0}]"
                                 .format(','.join(typlist)))

            if self.format_version > 108:
                self.varlist = [self._null_terminate(self.path_or_buf.read(33))
                                for i in range(self.nvar)]
            else:
                self.varlist = [self._null_terminate(self.path_or_buf.read(9))
                                for i in range(self.nvar)]
            self.srtlist = struct.unpack(
                self.byteorder + ('h' * (self.nvar + 1)),
                self.path_or_buf.read(2 * (self.nvar + 1))
            )[:-1]
            if self.format_version > 113:
                self.fmtlist = [self._null_terminate(self.path_or_buf.read(49))
                                for i in range(self.nvar)]
            elif self.format_version > 104:
                self.fmtlist = [self._null_terminate(self.path_or_buf.read(12))
                                for i in range(self.nvar)]
            else:
                self.fmtlist = [self._null_terminate(self.path_or_buf.read(7))
                                for i in range(self.nvar)]
            if self.format_version > 108:
                self.lbllist = [self._null_terminate(self.path_or_buf.read(33))
                                for i in range(self.nvar)]
            else:
                self.lbllist = [self._null_terminate(self.path_or_buf.read(9))
                                for i in range(self.nvar)]
            if self.format_version > 105:
                self.vlblist = [self._null_terminate(self.path_or_buf.read(81))
                                for i in range(self.nvar)]
            else:
                self.vlblist = [self._null_terminate(self.path_or_buf.read(32))
                                for i in range(self.nvar)]

            # ignore expansion fields (Format 105 and later)
            # When reading, read five bytes; the last four bytes now tell you
            # the size of the next read, which you discard.  You then continue
            # like this until you read 5 bytes of zeros.

            if self.format_version > 104:
                while True:
                    data_type = struct.unpack(self.byteorder + 'b',
                                              self.path_or_buf.read(1))[0]
                    if self.format_version > 108:
                        data_len = struct.unpack(self.byteorder + 'i',
                                                 self.path_or_buf.read(4))[0]
                    else:
                        data_len = struct.unpack(self.byteorder + 'h',
                                                 self.path_or_buf.read(2))[0]
                    if data_type == 0:
                        break
                    self.path_or_buf.read(data_len)

            # necessary data to continue parsing
            self.data_location = self.path_or_buf.tell()

        self.has_string_data = len([x for x in self.typlist
                                    if type(x) is int]) > 0

        """Calculate size of a data record."""
        self.col_sizes = lmap(lambda x: self._calcsize(x), self.typlist)