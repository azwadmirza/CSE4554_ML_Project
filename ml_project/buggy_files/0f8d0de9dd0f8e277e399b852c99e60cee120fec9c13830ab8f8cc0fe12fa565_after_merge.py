    def _write_data_nodates(self):
        data = self.datarows
        byteorder = self._byteorder
        TYPE_MAP = self.TYPE_MAP
        typlist = self.typlist
        for row in data:
            #row = row.squeeze().tolist() # needed for structured arrays
            for i, var in enumerate(row):
                typ = ord(typlist[i])
                if typ <= 244:  # we've got a string
                    if var is None or var == np.nan:
                        var = _pad_bytes('', typ)
                    if len(var) < typ:
                        var = _pad_bytes(var, typ)
                    if compat.PY3:
                        self._write(var)
                    else:
                        self._write(var.encode(self._encoding))
                else:
                    try:
                        self._file.write(struct.pack(byteorder + TYPE_MAP[typ],
                                                     var))
                    except struct.error:
                        # have to be strict about type pack won't do any
                        # kind of casting
                        self._file.write(struct.pack(byteorder+TYPE_MAP[typ],
                                         self.type_converters[typ](var)))