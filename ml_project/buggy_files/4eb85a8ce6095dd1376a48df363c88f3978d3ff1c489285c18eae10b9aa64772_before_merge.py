    def decode(self, variable, name=None):
        dims, data, attrs, encoding = unpack_for_decoding(variable)

        if 'missing_value' in attrs:
            # missing_value is deprecated, but we still want to support it as
            # an alias for _FillValue.
            if ('_FillValue' in attrs and
                not utils.equivalent(attrs['_FillValue'],
                                     attrs['missing_value'])):
                raise ValueError("Conflicting _FillValue and missing_value "
                                 "attrs on a variable {!r}: {} vs. {}\n\n"
                                 "Consider opening the offending dataset "
                                 "using decode_cf=False, correcting the "
                                 "attrs and decoding explicitly using "
                                 "xarray.decode_cf()."
                                 .format(name, attrs['_FillValue'],
                                         attrs['missing_value']))
            attrs['_FillValue'] = attrs.pop('missing_value')

        if '_FillValue' in attrs:
            raw_fill_value = pop_to(attrs, encoding, '_FillValue', name=name)
            encoded_fill_values = [
                fv for fv in np.ravel(raw_fill_value) if not pd.isnull(fv)]

            if len(encoded_fill_values) > 1:
                warnings.warn("variable {!r} has multiple fill values {}, "
                              "decoding all values to NaN."
                              .format(name, encoded_fill_values),
                              SerializationWarning, stacklevel=3)

            dtype, decoded_fill_value = dtypes.maybe_promote(data.dtype)

            if encoded_fill_values:
                transform = partial(_apply_mask,
                                    encoded_fill_values=encoded_fill_values,
                                    decoded_fill_value=decoded_fill_value)
                data = lazy_elemwise_func(data, transform, dtype)

        return Variable(dims, data, attrs, encoding)