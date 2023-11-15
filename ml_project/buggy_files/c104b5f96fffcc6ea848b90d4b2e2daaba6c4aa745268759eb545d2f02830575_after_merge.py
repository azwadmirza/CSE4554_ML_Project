    def write_registers(self, address, values, **kwargs):
        """
        Write list of `values` to registers starting at `address`.

        :param address: register offset to write to
        :param value: list of register value to write (comma seperated)
        :param unit: The slave unit this request is targeting
        :return:
        """
        resp = super(ExtendedRequestSupport, self).write_registers(
            address, values, **kwargs)
        return resp