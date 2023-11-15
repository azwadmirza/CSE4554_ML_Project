    def write_coils(self, address, values, **kwargs):
        """
        Write `value` to coil at `address`.

        :param address: coil offset to write to
        :param value: list of bit values to write (comma seperated)
        :param unit: The slave unit this request is targeting
        :return:
        """
        resp = super(ExtendedRequestSupport, self).write_coils(
            address, values, **kwargs)
        return resp