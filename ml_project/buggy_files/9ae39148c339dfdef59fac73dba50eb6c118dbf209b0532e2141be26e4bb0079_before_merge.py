    def prepare_variable(self, name, variable, check_encoding=False,
                         unlimited_dims=None):

        attrs = variable.attrs.copy()
        dims = variable.dims
        dtype = variable.dtype
        shape = variable.shape

        fill_value = _ensure_valid_fill_value(attrs.pop('_FillValue', None),
                                              dtype)
        if variable.encoding == {'_FillValue': None} and fill_value is None:
            variable.encoding = {}

        encoding = _extract_zarr_variable_encoding(
            variable, raise_on_invalid=check_encoding)

        encoded_attrs = OrderedDict()
        # the magic for storing the hidden dimension data
        encoded_attrs[_DIMENSION_KEY] = dims
        for k, v in iteritems(attrs):
            encoded_attrs[k] = self.encode_attribute(v)

        zarr_array = self.ds.create(name, shape=shape, dtype=dtype,
                                    fill_value=fill_value, **encoding)
        zarr_array.attrs.put(encoded_attrs)

        return zarr_array, variable.data