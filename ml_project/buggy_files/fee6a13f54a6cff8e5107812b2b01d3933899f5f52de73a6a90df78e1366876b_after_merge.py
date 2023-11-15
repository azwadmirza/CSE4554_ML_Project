    def encode(self, variable, name=None):
        dims, data, attrs, encoding = unpack_for_encoding(variable)

        if encoding.get('_FillValue') is not None:
            fill_value = pop_to(encoding, attrs, '_FillValue', name=name)
            if not pd.isnull(fill_value):
                data = duck_array_ops.fillna(data, fill_value)

        return Variable(dims, data, attrs, encoding)