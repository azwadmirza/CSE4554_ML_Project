    def _deserialize(self, value, attr, data, **kwargs):  # pylint: disable=unused-argument
        if not is_0x_prefixed(value):
            self.fail("missing_prefix")

        if not is_checksum_address(value):
            self.fail("invalid_checksum")

        try:
            value = to_canonical_address(value)
        except ValueError:
            self.fail("invalid_data")

        if len(value) != 20:
            self.fail("invalid_size")

        if value == NULL_ADDRESS_BYTES:
            self.fail("null_address")

        return value