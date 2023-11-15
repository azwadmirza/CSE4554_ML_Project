    def __init__(self, ds, *args, **kwargs):
        self._vector_fields = dict(self._vector_fields)
        self._fields = ds._field_spec
        self._ptypes = ds._ptype_spec
        self.data_files = set([])
        gformat = _get_gadget_format(ds.parameter_filename, ds._header_size)
        # gadget format 1 original, 2 with block name
        self._format = gformat[0]
        self._endian = gformat[1]
        super(IOHandlerGadgetBinary, self).__init__(ds, *args, **kwargs)